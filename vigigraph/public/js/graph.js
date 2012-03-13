// Copyright (C) 2006-2011 CS-SI
// License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

var refresh_delay = 30;
var graphs = [];

var old_fragment = '';
var skip_detection = 0;

var logger = new Log;
logger.enableLog();

var Graph = new Class({
    Implements: [Events, Options],

    options: {
        duration: 86400,
        start: null,
        autoRefresh: 0,
        refreshDelay: null,
        left: null,
        top: null,
        overlap: 10    // Pourcentage de recouvrement (voir #730)
    },

    initialize: function (options, host, graph) {
        this.setOptions(options);
        this.host = host;
        this.graph = graph;
        this.refreshTimer = null;
        this.destroyed = false;

        new Request.JSON({
            url: app_path + 'rpc/startTime',
            onSuccess: function (data) {
                this.startTime = data.starttime.toInt();
            }.bind(this)
        }).get({'host': this.host});

        var toolbar = new Jx.Toolbar({position:'top'});
        var periods = [
            [_('Last 12 hours'),    12],
            [_('Last 24 hours'),    24],
            [_('Last 48 hours'),    48],
            [_('Last 7 days'),      7*24],
            [_('Last 14 days'),     14*24],
            [_('Last month'),       30*24],
            [_('Last 3 months'),    3*30*24],
            [_('Last 6 months'),    6*30*24],
            [_('Last year'),        365*24]
        ];

        var timeframe = new Jx.Menu({
            label: _("Timeframe"),
            image: app_path + 'images/history.png',
            tooltip: _("Timeframe menu")
        });

        periods.each(function (period) {
            var menuItem = new Jx.Menu.Item({
                label: period[0]
            });
            menuItem.options.period = period[1] * 60 * 60;
            menuItem.addEvent('click', function () {
                this[0].options.start = null;
                this[0].options.duration = (this[1].options.period).toInt();
                this[0].updateGraph();
            }.bind([this, menuItem]));
            timeframe.add(menuItem);
        }, this);

        // Indicateur d'alerte en cas d'erreur
        var alert_msg = _(
            'Could not load the graph for "%(graph)s" on "%(host)s". ' +
            'Make sure VigiRRD is running and receives performance data.'
        );
        // Le pattern donné à substitute permet de garder une syntaxe
        // cohérente avec Python (facilite le travail des traducteurs).
        alert_msg = alert_msg.substitute({
                'graph': this.graph,
                'host': this.host
            }, (/\\?%\(([^()]+)\)s/g));
        this.alert_indicator = new Element("img");
        this.alert_indicator.addClass("alert-indicator");
        this.alert_indicator.setProperty("src", app_path + 'images/messagebox_warning.png');
        this.alert_indicator.setProperty("title", alert_msg);

        this.indicators = new Jx.Menu({
            label: _("Export to CSV"),
            image: app_path + 'images/document-export.png',
            tooltip: _("Export the content of this graph to CSV")
        });

        new Request.JSON({
            url: app_path + 'rpc/getIndicators',
            onSuccess: function (data) {
                data.items.each(function (item) {
                    this.indicators.add(new Jx.Menu.Item({
                        name: item[0],
                        label: item[1],
                        onClick: this.exportCSV.bind(this),
                        indicator: true
                    }));
                }, this);

                this.indicators.add(new Jx.Menu.Item({
                    label: _('All'),
                    onClick: this.exportCSV.bind(this),
                    indicator: false
                }));
            }.bind(this)
        }).get({
            'host': this.host,
            'graph': this.graph
        });

        this.refresh_button = new Jx.Button({
            image: app_path + 'images/refresh.png',
            tooltip: _("Automatically refresh the graph"),
            toggle: true,
            onDown: function() {
                // On s'assure qu'il n'y a pas déjà un timer lancé.
                if ($chk(this.refreshTimer))
                    return;
                var delay =
                    this.options.refreshDelay ||
                    window.refresh_delay;
                this.refreshTimer =
                    this.updateGraph.periodical(delay * 1000, this);
                this.options.autoRefresh = 1;
                logger.log((_(
                    'Auto-refresh enabled on graph "{graph}" for host "{host}"'
                    )).substitute({
                        'graph': this.graph,
                        'host': this.host
                    }));
                window.updateURI();
            }.bind(this),
            onUp: function() {
                clearInterval(this.refreshTimer);
                // clearInterval arrête le timer, mais n'invalide pas
                // la référence, ce dont on a besoin (cf. onDown).
                this.refreshTimer = null;
                this.options.autoRefresh = 0;
                logger.log((_(
                    'Auto-refresh disabled on graph "{graph}" for host "{host}"'
                    )).substitute({
                        'graph': this.graph,
                        'host': this.host
                    }));
                window.updateURI();
            }.bind(this)
        });

        this.zoom_in = new Jx.Button({
            image: app_path + 'images/zoom-in.png',
            tooltip: _("Zoom in"),
            onClick: function() {
                this.updateZoom(true);
            }.bind(this)
        });

        this.zoom_out = new Jx.Button({
            image: app_path + 'images/zoom-out.png',
            tooltip: _("Zoom out"),
            onClick: function() {
                this.updateZoom(false);
            }.bind(this)
        });

        toolbar.add(
            this.refresh_button,
            timeframe,
            new Jx.Button({
                image: app_path + 'images/start.png',
                tooltip: _("Graph start"),
                onClick: function() {
                    this.options.start = this.startTime;
                    this.updateGraph();
                }.bind(this)
            }),
            new Jx.Button({
                image: app_path + 'images/previous.png',
                tooltip: _("Previous section"),
                onClick: function() {
                    this.options.start =
                        this.getStartTime() -
                        this.options.duration +
                        (this.options.overlap * this.options.duration / 100).toInt();
                    this.updateGraph();
                }.bind(this)
            }),
            new Jx.Button({
                image: app_path + 'images/next.png',
                tooltip: _("Next section"),
                onClick: function() {
                    this.options.start =
                        this.getStartTime() +
                        this.options.duration -
                        (this.options.overlap * this.options.duration / 100).toInt();
                    this.updateGraph();
                }.bind(this)
            }),
            new Jx.Button({
                image: app_path + 'images/end.png',
                tooltip: _("Graph end"),
                onClick: function() {
                    this.options.start = null;
                    this.updateGraph();
                }.bind(this)
            }),
            this.zoom_in,
            this.zoom_out,
            this.indicators,
            new Jx.Button({
                image: app_path + 'images/document-print-small.png',
                tooltip: _("Print graph"),
                onClick: this.print.bind(this)
            })
        );

        var label = _("Graph for \"%(graph)s\" on \"%(host)s\"");
        // Le pattern donné à substitute permet de garder une syntaxe
        // cohérente avec Python (facilite le travail des traducteurs).
        label = label.substitute({
                'graph': this.graph,
                'host': this.host
            }, (/\\?%\(([^()]+)\)s/g));

        this.graph_window = new Jx.Dialog({
            label: label,
            modal: false,
            move: true,
            close: true,
            horizontal: this.options.left + ' left',
            vertical: this.options.top + ' top',
            width: 575,
            height: 75,
            vertical_overflow: true,
            horizontal_overflow: true,
            toolbars: [toolbar]
        });
        // Empêche l'affichage d'une barre de défilement vertical
        // désactivée sous Chromium.
        this.graph_window.content.setStyle('overflow', 'hidden');

        this.alert_indicator.inject(this.graph_window.content.parentNode);

        // mise à jour
        this.updateGraph();
        this.graph_window.open();

        this.refresh_button.setActive(parseInt(this.options.autoRefresh, 10));

        var onClose = function () {
            if (this.destroyed) return;
            this.destroyed = true;
            this.graph_window.domObj.dispose();
            window.graphs.erase(this);
            window.updateURI();
        };

        this.graph_window.addEvent('close', onClose.bind(this));
        // sizeChange est déclenché à la fois après un redimensionnement
        // et après un déplacement. Ce cas est mal documenté dans JxLib.
        this.graph_window.addEvent('sizeChange', this.dialogMoved.bind(this));

        // Simule un déplacement de la fenêtre,
        // pour mettre à jour les coordonnées.
        this.dialogMoved();
        window.graphs.push(this);
        return this;
    },

    destroy: function () {
        this.graph_window.close();
    },

    dialogMoved: function () {
        // Repris de l'API interne de JxLib (création du Drag).
        this.options.left = parseInt(this.graph_window.domObj.style.left, 10);
        this.options.top = parseInt(this.graph_window.domObj.style.top, 10);
        window.updateURI();
    },

    updateZoom: function (zoom_in) {
        var start = this.options.start;
        var factor = zoom_in ? 0.5 : 2;
        this.options.duration = parseInt(this.options.duration, 10);
        if (start !== null) {
            // On zoom sur la partie centrale du graphe.
            if (zoom_in) start += this.options.duration * 0.25;
            // On dézoome "par les 2 côtés".
            else start -= this.options.duration * 0.5;
            this.options.start = start;
        }
        this.options.duration *= factor;
        // Période minimale d'affichage : 1 minute.
        if (this.options.duration < 60)
            this.options.duration = 60;
        // On (dés)active le bouton de zoom en avant au besoin.
        this.zoom_in.setEnabled(this.options.duration != 60);
        this.updateGraph();
    },

    getStartTime: function () {
        var start = this.options.start;
        if (start === null)
            // On génère un horodatage UNIX correspondant
            // à l'heure courante en UTC.
            start = (new Date() / 1000).toInt() - this.options.duration;
        if (start < 0)
            return 0;
        return start;
    },

    exportCSV: function (menuItem) {
        var uri = new URI(app_path + 'vigirrd/' +
            encodeURIComponent(this.host) + '/export');

        var start = this.getStartTime();

        uri.setData({
            host: this.host,
            graphtemplate: this.graph,
            start: start,
            end: start + this.options.duration,
            // Décalage par rapport à UTC, ex: 60 = UTC+01:00.
            timezone: (new Date()).getTimezoneOffset(),
            nocache: (new Date() / 1)
        });

        if (menuItem.options.indicator)
            uri.setData({ds: menuItem.options.name}, true);

        window.open(uri.toString());
    },

    // Cette fonction est aussi utilisée dans print.js
    // pour gérer l'impression globale.
    getPrintParams: function () {
        var img = this.graph_window.content.getElement('img');
        var img_uri = new URI(img.src);
        var params = img_uri.getData();
        return {
            host: params.host,
            start: params.start,
            duration: params.duration,
            graph: params.graphtemplate,
            nocache: params.nocache
        };
    },

    print: function () {
        var uri = new URI(app_path + 'rpc/graphsList');
        uri.setData({graphs: [this.getPrintParams()]});
        var print_window = window.open(uri.toString());
        print_window.onload = function () {
            this.print();
        }.bind(print_window);
    },

    updateGraph: function () {
        var uri = new URI(app_path + 'vigirrd/' +
            encodeURIComponent(this.host) + '/graph.png');

        var start = this.getStartTime();

        uri.setData({
            host: this.host,
            start: start,
            duration: this.options.duration,
            graphtemplate: this.graph,
            // Permet d'empêcher la mise en cache du graphe.
            // Nécessaire car le graphe évolue dynamiquement au fil de l'eau.
            nocache: (new Date() / 1)
        });
        // On génère dynamiquement une balise "img" pour charger le graphe.
        this.graph_window.setContent(
            '<img src="' + uri.toString() + '"/' + '>');
        var img = this.graph_window.content.getElement('img');
        img.addEvent('load', function () {
            this[0].graph_window.resize(
                this[1].width + 25,
                this[1].height + 73
            );
            this[0].hideAlert();
        }.bind([this, img]));
        img.addEvent('error', function () {
            // if (this.refreshTimer) clearInterval(this.refreshTimer);
            this.showAlert();
            //this.graph_window.close();
        }.bind(this));
    },

    showAlert: function() {
        this.alert_indicator.setStyle("display", "block");
        var zindex = parseInt(this.graph_window.domObj.getStyle("z-index"), 10) + 1;
        this.alert_indicator.setStyle("z-index", zindex);
        return;
    },

    hideAlert: function() {
        this.alert_indicator.setStyle("display", "none");
    }
});

var updateURI = function () {
    var graphs_uri = [];
    var uri = new URI();

    // Section critique.
    window.skip_detection++;
    uri.set('fragment', '');

    window.graphs.each(function (graph) {
        var props = new Hash(graph.options);
        props.extend({host: graph.host, graph: graph.graph});
        // Sous Firefox, l'apostrophe n'est pas échappée via JavaScript,
        // alors qu'elle l'est par le navigateur dans l'URL.
        // Afin d'éviter une boucle de rechargement infinie, on échappe
        // manuellement l'apostrophe.
        this.push(props.toQueryString().replace(/'/, '%27'));
    }, graphs_uri);

    uri.setData({'graphs': graphs_uri, safety: 1}, false, 'fragment');
    uri.go();
    window.old_fragment = uri.toString();

    // Fin de section critique.
    window.skip_detection--;
};

var update_visible_graphs = function (new_fragment) {
    // On réouvre les graphes précédemment chargés.
    var new_graphs = [];
    var qs = new Hash(new_fragment.get('fragment').parseQueryString());
    if (qs.has('graphs')) {
        new_graphs = (new Hash(qs.get('graphs'))).getValues();
    }

    // Section critique.
    window.skip_detection++;

    var prev_graphs = window.graphs;
    window.graphs = [];
    prev_graphs.each(function (graph) { graph.destroy(); });

    new_graphs.each(function (graph) {
        var uri = new URI('?' + graph);
        var qs = new Hash(uri.getData());
        if (qs.has('host') && qs.has('graph')) {
            var options = new Hash();
            var params = [
                'start',
                'duration',
                'left',
                'top',
                'autoRefresh',
                'refreshDelay'
            ];

            params.each(function (param) {
                if (this[0].has(param))
                    this[1].set(param, (this[0].get(param)).toInt());
            }, [qs, options]);

            new Graph(
                options.getClean(),
                qs.get('host'),
                qs.get('graph')
            );
        }
    });

    window.updateURI();

    // Fin de section critique.
    window.skip_detection--;

    if (window.graphs.length == 1) {
        new Request.JSON({
            url: app_path + 'rpc/selectHostAndGraph',
            onSuccess: function (results) {
                window.toolbar.host_picker.setItem(results.idhost, this[0]);
                window.toolbar.graph_picker.idselection = results.idgraph;
                window.toolbar.graph_picker.setLabel(this[1]);
            }.bind([
                window.graphs[0].host,
                window.graphs[0].graph
            ])
        }).get({
            host: window.graphs[0].host,
            graph: window.graphs[0].graph
        });
    }
};

var hash_change_detector = function() {
    var new_fragment;

    // Pour les moments où on a besoin de mettre à jour
    // volontairement l'URI (à l'ouverture d'un graphe).
    if (window.skip_detection) return;

    // Force mootools à analyser l'URL courante de nouveau,
    // ce qui mettra à jour la partie "fragment" de l'URI.
    URI.base = new URI(
        document.getElements('base[href]', true).getLast(),
        {base: document.location}
    );

    new_fragment = new URI();
    if (old_fragment.toString() != new_fragment.toString()) {
        update_visible_graphs(new_fragment, old_fragment);
    }
};

if ('onhashchange' in window) {
    window.onhashchange = hash_change_detector;
} else {
    hash_change_detector.periodical(100);
}

window.addEvent('load', function () {
    new Request.JSON({
        url: app_path + 'rpc/tempoDelayRefresh',
        onSuccess: function (data) {
            window.refresh_delay = data.delay;
        }
    }).get();

    hash_change_detector();
});
