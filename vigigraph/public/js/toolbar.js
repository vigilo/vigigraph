Jx.Button.SelectorFlyout = new Class({
    Extends: Jx.Button.Flyout,

    initialize: function (options, url, hostid) {
        this.parent(options);
        this.idselection = null;
        this.tree = new TreeGroup({
            title: this.options.label,
            url: url,
            hostid: hostid
        });
        this.tree.addEvent('select', this.selectItem.bind(this));
   },

    setItem: function (id, label) {
        this.idselection = id;
        this.setLabel(label);
        this.fireEvent("select");
    },

    selectItem: function (item) {
        this.setItem(item.options.data, item.options.label);
    },

    clicked: function (e) {
        if (!this.options.enabled)
            return;
        this.tree.selectGroup();
    }
});

var Toolbar = new Class({
    initialize: function () {
        this.jxtoolbar = new Jx.Toolbar({
            parent: $('toolbar')
        });

        this.global_refresh = new Jx.Button({
            tooltip: _('Globally change auto-refresh setting'),
            image: app_path + 'images/refresh-all.png',
            toggle: true,
            onDown: function () {
                window.graphs.each(function (graph) {
                    graph.refresh_button.setActive(1);
                }, this.global_refresh);
            }.bind(this),
            onUp: function () {
                window.graphs.each(function (graph) {
                    graph.refresh_button.setActive(0);
                }, this.global_refresh);
            }.bind(this)
        });
        this.jxtoolbar.add(this.global_refresh);

        this.host_label = new Jx.Toolbar.Item(this.createLabel(_('Host:')));

        this.host_picker = new Jx.Button.SelectorFlyout({
                label: _('Select a host'),
                tooltip: _('Click me to select another host')
            },
            app_path + 'rpc/hosttree',
            null
        );

        this.host_picker.addEvent("select", function() {
            var idselection = this.host_picker.idselection;
            if (this.graph_picker.tree.options.hostid != idselection) {
                this.graph_picker.tree.options.hostid = idselection;
                this.graph_picker.tree.redraw();
                this.graph_picker.setItem(0, this.graph_picker.options.label);
            }
            this.graph_picker.setEnabled(1);
            this.show_graph.setEnabled(1);
        }.bind(this));

        this.show_nagios = new Jx.Button({
            label: _('Nagios page'),
            tooltip: _('Display Nagios page for the selected host'),
            toggle: false,
            onClick: function () {
                var uri = new URI(
                    app_path + 'nagios/' +
                    encodeURIComponent(this.host_picker.getLabel()) +
                    '/cgi-bin/status.cgi'
                );
                uri.setData({
                    host: this.host_picker.getLabel(),
                    style: 'detail',
                    supNav: 1
                });
                window.open(uri.toString());
            }.bind(this)
        })

        this.jxtoolbar.add(this.host_label);
        this.jxtoolbar.add(this.host_picker);
        this.jxtoolbar.add(this.show_nagios);

        var separator = new Jx.Toolbar.Separator();
        this.jxtoolbar.add(separator);

        this.graph_label = new Jx.Toolbar.Item(this.createLabel(_('Graph:')));

        this.graph_picker = new Jx.Button.SelectorFlyout({
                label: _('Select a graph'),
                tooltip: _('Click me to select another graph'),
                enabled: false
            },
            app_path + 'rpc/graphtree',
            null
        );

        this.show_graph = new Jx.Button({
            label: _('Graph'),
            tooltip: _('Display the contents of the selected graph'),
            toggle: false,
            enabled: false,
            onClick: function () {
                 new Graph(
                    {autoRefresh: this.global_refresh.isActive() ? 1 : 0},
                    this.host_picker.getLabel(),
                    this.graph_picker.getLabel()
                );
            }.bind(this)
        })

        this.jxtoolbar.add(this.graph_label);
        this.jxtoolbar.add(this.graph_picker);
        this.jxtoolbar.add(this.show_graph);
    },

    // Retourne un objet opaque qui possède un label,
    // et peut être ajouté à une Jx.Toolbar via Jx.Toolbar.Item.
    createLabel: function (label) {
        var container, content, span;

        container = new Element('div', {'class': 'jxButtonContainer'});
        content = new Element('span', {'class': 'jxButtonContent'});
        span = new Element('span', {
            'class': 'jxButtonLabel',
            text: label
        });
        span.setStyles({cursor: 'default'});

        span.inject(content);
        content.inject(container);

        return container;
    }
});

toolbar = null;
window.addEvent('load', function () {
    window.toolbar = new Toolbar();
});
