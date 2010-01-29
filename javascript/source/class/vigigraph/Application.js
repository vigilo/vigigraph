/* ************************************************************************

   Vigigraph User Interface
   Copyright: 2007-2009 CS-SI <http://www.c-s.fr>

   License: GPLv2+

   Authors: Arnaud MAZIN <arnaud.mazin@c-s.fr>
            Aurelien BOMPARD <aurelien.bompard@c-s.fr>
            Thomas BURGUIERE <thomas.burguiere@c-s.fr>
            Francis LAHEUGUERE <francis.laheuguere@c-s.fr>

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.
  
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
  
   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

************************************************************************ */

/* ************************************************************************

//#require(qx.event.handler.DragAndDropHandler)
//#resource(vigigraph.image:image)

// List all static resources that should be copied into the build version,
// if the resource filter option is enabled (default: disabled)
//#embed(qx.icontheme/32/status/dialog-information.png)
//#embed(vigigraph.image/test.png)

************************************************************************ */

var urls = {
    "maingroups": "/rpc/maingroups",
    "hostgroups": "/rpc/hostgroups",
    "hosts": "/rpc/hosts",
    // NOTE Graph Groups (frontend) -> ServiceGroup (backend)
    "graphgroups": "/rpc/servicegroups",
    "graphs": "/rpc/graphs",
    "selectHostAndService": "/rpc/selectHostAndService",
    "searchHostAndService": "/rpc/searchHostAndService",
    "subPage": "/rpc/subPage",
    "getImage": "/rpc/getImage",
    "getStartTime": "/rpc/getStartTime",
    "getIdHost": "/rpc/getIdHost",
    "getIdService": "/rpc/getIdService",
    "graphsList": "/rpc/graphsList",
    "tempoDelayRefresh": "/rpc/tempoDelayRefresh",
    "getIndicators": "/rpc/getIndicators",
    "exportCSV": "/rpc/exportCSV"
};

/**
 * Main Application (based on the qooxdoo skeleton)
 */
qx.Class.define("vigigraph.Application",
{
  extend : qx.application.Gui,


  /*
  *****************************************************************************
     MEMBERS
  *****************************************************************************
  */

  members :
  {
    /**
     * Main function.
     *
     * @type member
     */
    main : function()
    {
      this.base(arguments);

      // Define alias for vigigraph resource path
      qx.io.Alias.getInstance().add("vigigraph", qx.core.Setting.get("vigigraph.resourceUri"));

      // Change the window title
      document.title = this.tr("Vigilo Graphic");

      // Host picker
      var w1 = new qx.ui.window.Window(this.tr("Host Picker"), "icon/16/devices/network-wired.png");
      w1.setSpace(20, 250, 48, 102);
      w1.setShowClose(false);
      w1.setShowMinimize(false);
      w1.setShowMaximize(false);
      w1.setResizable(false, false, false, false);

      var gl = new qx.ui.layout.GridLayout;
      gl.setDimension("auto", "auto");
      gl.setColumnCount(4);
      gl.setRowCount(6);			//Number of rows in the main window
      gl.setVerticalSpacing(4);
      gl.setHorizontalSpacing(2);

      gl.setColumnWidth(0, 100);
      gl.setColumnWidth(1, 180);
      gl.setColumnWidth(2, 18);
      gl.setColumnWidth(3, 18);

      //gl.setColumnHorizontalAlignment(0, "right");
      gl.setColumnVerticalAlignment(0, "middle");

      gl.setRowHeight(0, 20);
      gl.setRowHeight(1, 20);
      gl.setRowHeight(2, 20);
      gl.setRowHeight(3, 20);
      gl.setRowHeight(4, 20);
      gl.setRowHeight(5, 20);

      gl.add(new qx.ui.basic.Label(this.tr("Main Group")), 0, 0);
      gl.add(new qx.ui.basic.Label(this.tr("Host Group")), 0, 1);
      gl.add(new qx.ui.basic.Label(this.tr("Host Name")), 0, 2);
      gl.add(new qx.ui.basic.Label(this.tr("Graph Group")), 0, 3);
      gl.add(new qx.ui.basic.Label(this.tr("Graph Name")), 0, 4);

      var combo1 = new qx.ui.form.ComboBox;
      var combo2 = new qx.ui.form.ComboBox;
      var combo3 = new qx.ui.form.ComboBox;
      var combo4 = new qx.ui.form.ComboBox;
      var combo5 = new qx.ui.form.ComboBox;

      var r1=new qx.ui.form.Button("","icon/16/actions/view-refresh.png");
      r1.setToolTip(new qx.ui.popup.ToolTip(this.tr("Refresh")));
      var r2=new qx.ui.form.Button("","icon/16/actions/view-refresh.png");
      r2.setToolTip(new qx.ui.popup.ToolTip(this.tr("Refresh")));
      var r3=new qx.ui.form.Button("","icon/16/actions/view-refresh.png");
      r3.setToolTip(new qx.ui.popup.ToolTip(this.tr("Refresh")));
      var r4=new qx.ui.form.Button("","icon/16/actions/view-refresh.png");
      r4.setToolTip(new qx.ui.popup.ToolTip(this.tr("Refresh")));
      var r5=new qx.ui.form.Button("","icon/16/actions/view-refresh.png");
      r5.setToolTip(new qx.ui.popup.ToolTip(this.tr("Refresh")));

      var b1=new qx.ui.form.Button("","icon/16/actions/zoom.png");
      b1.setToolTip(new qx.ui.popup.ToolTip(this.tr("Search")));
      var b3=new qx.ui.form.Button("","icon/16/actions/go-right.png");
      b3.setToolTip(new qx.ui.popup.ToolTip(this.tr("Show Nagios page")));
      b3.setEnabled(false);
      var b5=new qx.ui.form.Button("","icon/16/actions/go-right.png");
      b5.setToolTip(new qx.ui.popup.ToolTip(this.tr("Show graph")));
      b5.setEnabled(false);

      var bp=new qx.ui.form.Button("","icon/16/actions/document-print.png");
      bp.setToolTip(new qx.ui.popup.ToolTip(this.tr("Print")));
      bp.setEnabled(true);

      gl.add(r1,2,0);
      gl.add(r2,2,1);
      gl.add(r3,2,2);
      gl.add(r4,2,3);
      gl.add(r5,2,4);
      
      gl.add(b1,3,0);
      gl.add(b3,3,2);
      gl.add(b5,3,4);

      gl.add(bp,3,5);

      _updateServerGroupList();

      var w2 = undefined;

      function getIndexWindow (cdi, w)
      {
        // var cdi = qx.ui.core.ClientDocument.getInstance();
        var index_l = -1;
        if (cdi)
        {
          var nb = cdi.getChildren().length;
          for (i = 0; i < nb; i++)
          {
            var c_l = cdi.getChildren()[i];
            if (c_l)
            {
              if (c_l.name == "qx.ui.window.Window")
              {
                caption_l = c_l.getCaption();
                if (c_l == w)
                {
                  index_l = i;
                }
              }
            }
          }
        }
        return index_l;
      }

      function tempoFire(Delay)
      {
        var a = setTimeout(tempoFall, Delay);
      }

      function tempoFall()
      {
        if ( w2 != undefined)
        {
          w2.close();
        }
      }

      // Buttons
      bp.addEventListener("execute",function(e) {
        var nb = document.images.length;

        // liste src
        var index_p = -1;
        var src_l = "";
        var src_tab = new Array;
        var j = 0;
        for (i = 0; i < nb; i++)
        {
          src_l = document.images[i].src;

          // graphe rrd ?
          pos = src_l.search("/rrdgraph.py");
          if (pos != -1)
          {
            src_tab[j] = encodeURIComponent(src_l);
            j += 1; 
          }
        }

        // impression à partir nouvelle fenêtre
        var lh = src_tab.length;
        if (lh > 0)
        {
          var url = urls.graphsList;
          url += "?";
          for (i = 0; i < lh; i++)
          {
            if (i > 0)
            {
              url += "&";
            }
            url += i;
            url += "=";
            url += src_tab[i];
          }

          w2 = window.open(url);
          w2.onload = function(){
            w2.print();
            wDelay = 1000;
            tempoFire(wDelay);
          }
        }
      });

      b3.addEventListener("execute",function(e) {
        var win = new qx.client.NativeWindow(urls.subPage+"?host="+combo3.getSelected().getLabel());
        win.setDimension(800,600);
        win.setDependent(false);
        win.open();
      });

      b5.addEventListener("execute",function(e) { 
        var host=combo3.getSelected().getLabel();
        var graph=combo5.getSelected().getLabel();
        this.openGraph(host, graph, null, null, true);
      }, this);
      
      b1.addEventListener("execute",function(e) { 
        var w_search = new qx.ui.window.Window(this.tr("Search"), "icon/16/actions/zoom.png");
        w_search.addToDocument();
        w_search.set({
                      showMinimize : false,
                      showMaximize : false,
                      resizable    : true
                     });
        var w_search_v = new qx.ui.layout.VerticalBoxLayout();
        w_search_v.setWidth("100%");
        w_search_v.setHeight("100%");
        w_search_v.setHorizontalChildrenAlign("center");
        w_search.add(w_search_v);
        var w_search_h = new qx.ui.layout.HorizontalBoxLayout();
        w_search_h.auto()
        w_search_h.setVerticalChildrenAlign("middle");
        w_search_h.setPadding(2, 5, 5, 5);
        w_search_v.add(w_search_h);
        w_search_h.add(new qx.ui.basic.Label(this.tr("Host:")));
        var search_host = new qx.ui.form.TextField();
        w_search_h.add(search_host);
        search_host.setMarginRight(5);
        search_host.setLiveUpdate(true);
        search_host.tabIndex = 1;
        search_host.setToolTip(new qx.ui.popup.ToolTip(this.tr("Search for a host (\"*\" for all, 100 max)")));
        w_search_h.add(new qx.ui.basic.Label(this.tr("Service:")));
        var search_service = new qx.ui.form.TextField();
        w_search_h.add(search_service);
        search_service.setMarginRight(5);
        search_service.setLiveUpdate(true);
        search_service.tabIndex = 2;
        search_service.setToolTip(new qx.ui.popup.ToolTip(this.tr("Search for a service (\"*\" for all, 100 max)")));
        var search_button=new qx.ui.form.Button("","icon/16/actions/zoom.png");
        search_button.setWidth(20);
        search_button.setHeight(20);
        w_search_h.add(search_button);
        var search_results_model = new qx.ui.table.model.Simple();
        search_results_model.setColumns([ this.tr("Host"), this.tr("Service") ]);
        var custom = {
          tableColumnModel :
            function(obj)
            {
              return new qx.ui.table.columnmodel.Resize(obj);
            }
        };
        var search_results = new qx.ui.table.Table(search_results_model, custom);
        search_results.hide();
        with (search_results) {
          set({ left:0, top:0, right:0, bottom: 10, width:"95%", height:"90%", border:"inset-thin" });
          //setMetaColumnCounts([1, -1]);
          getSelectionModel().setSelectionMode(qx.ui.table.selection.Model.SINGLE_SELECTION);
          setColumnVisibilityButtonVisible(false);
          setStatusBarVisible(false);
          var tcm = search_results.getTableColumnModel();
          var resizeBehavior = tcm.getBehavior();
          // This uses the set() method to set all attriutes at once; uses flex
          resizeBehavior.set(0, { width:"1*", minWidth:40, maxWidth:180  });
          resizeBehavior.set(1, { width:"1*", minWidth:40, maxWidth:180  });

          //// We could also set them individually:
          ////resizeBehavior.setWidth(1, "50%");
          ////resizeBehavior.setMinWidth(1, 100);
          ////resizeBehavior.setMaxWidth(1, 320);
        };
        w_search_v.add(search_results);
        //search_results.setLocation(10, 40);
        function _searchResultsUpdater(host,service)
        {
          var url = urls.searchHostAndService;
          if (host && service) { url = url+"?host="+host+"&service="+service };
          else if (host) { url = url+"?host="+host };
          else if (service) { url = url+"?service="+service };

          search_results_model.setData([]);
          var g=new qx.io.remote.Request(url,"GET","application/json");
          g.addEventListener("completed", function(e) {
            var rowData = [];
            r=e.getContent().items;
            for(var i=0,l=r.length ; i<l ; i++) // does not work in IE with "for (i in r)"
            {
              rowData.push(r[i]);
            }
            search_results_model.setData(rowData);
            search_results.show();
            //qx.log.Logger.ROOT_LOGGER.debug(rowData);
          });
          g.send();
        }
        function _chooseInCombos(host, host_main_group, host_sec_group, service, service_group) {
          function _selectItem(o, item) {
            var c_list = o.getList();
            var c_item = c_list.findStringExact(item);

            if (c_item) {
              o.setSelected(c_item);
            }
          }
          combo1.addEventListener("changeEnabled", function(e) { 
            if (e.getValue() == true) {
              e.getTarget().removeEventListener("changeEnabled", arguments.callee);
              _selectItem(e.getTarget(), host_main_group);
            }
          });
          combo2.addEventListener("changeEnabled", function(e) { 
            if (e.getValue() == true) {
              e.getTarget().removeEventListener("changeEnabled", arguments.callee);
              _selectItem(e.getTarget(), host_sec_group);
            }
          });
          combo3.addEventListener("changeEnabled", function(e) { 
            if (e.getValue() == true) {
              e.getTarget().removeEventListener("changeEnabled", arguments.callee);
              _selectItem(e.getTarget(), host); 
            }
          });
          if ((service) && (service_group)) {
            combo4.addEventListener("changeEnabled", function(e) {
              if (e.getValue() == true) {
                e.getTarget().removeEventListener("changeEnabled", arguments.callee);
                _selectItem(e.getTarget(), service_group); 
              }
            });
            combo5.addEventListener("changeEnabled", function(e) {
              if (e.getValue() == true) {
                e.getTarget().removeEventListener("changeEnabled", arguments.callee);
                _selectItem(e.getTarget(), service); 
              }
            });
          }
          _updateServerGroupList();
        }
        function _selectHostAndService(host, service, mainObj)
        {
          var url = urls.selectHostAndService;
          if (host && service) { url = url+"?host="+host+"&service="+service };
          else if (host) { url = url+"?host="+host };
          else if (service) { url = url+"?service="+service };

          var g=new qx.io.remote.Request(url,"GET","application/json");
          g.addEventListener("completed", function(e) {
            r=e.getContent().items;
            var host_main_group = r[0];
            var host_sec_group = r[1];

            if (r.length < 3) { 
              _chooseInCombos(host, host_main_group, host_sec_group, null, null);
            }
            else {
              var srv_group = r[2];
              _chooseInCombos(host, host_main_group, host_sec_group, service, srv_group);
              mainObj.openGraph(host, service, null, null, true);
            }
            //qx.log.Logger.ROOT_LOGGER.debug(rowData);
          });
          g.send();
        }
        // On selection, update the Host Picker and close the search window
        search_results.addEventListener("cellClick", function(e) {
          var row = e.getRow();
          var col = e.getColumn();
          var value_host = search_results_model.getValue(0, row);
          var value_service = search_results_model.getValue(1, row);
          if (!value_service) {
            _selectHostAndService(value_host, null, this);
          } else {
            _selectHostAndService(value_host, value_service, this);
          }
        }, this);
        // Give keyboard focus to the search field
        search_host.addEventListener("appear", function(e)
        {
          this.getInputElement().focus();
        }, search_host);
        // Submit events
        search_host.addEventListener("keydown", function(e) {
          if (e.getKeyIdentifier() == "Enter") {
            _searchResultsUpdater(search_host.getValue(), search_service.getValue());
          }
        });
        search_host.addEventListener("changeValue", function(e) {
          _searchResultsUpdater(search_host.getValue(), search_service.getValue());document.body.outerHTML
        });
        search_service.addEventListener("keydown", function(e) {
          if (e.getKeyIdentifier() == "Enter") {
            _searchResultsUpdater(search_host.getValue(), search_service.getValue());
          }
        });
        search_service.addEventListener("changeValue", function(e) {
          _searchResultsUpdater(search_host.getValue(), search_service.getValue());
        });
        // Submit button
        search_button.addEventListener("execute",function(e) {
          _searchResultsUpdater(search_host.getValue(), search_service.getValue());
        });
        w_search.open();
        w_search.setTop(w1.getTop());document.body.outerHTML
        w_search.setLeft(qx.html.Location.getPageBoxRight(w1.getElement()));
        // centerToBrowser does not work on window objects (breaks the buttons in the title bar)
        //w_search.centerToBrowser()
      }, this);
      // end of b1
      //////////////////////////////////////


      gl.add(combo1, 1, 0);
      gl.add(combo2, 1, 1);
      gl.add(combo3, 1, 2);
      gl.add(combo4, 1, 3);
      gl.add(combo5, 1, 4);
      w1.add(gl);
      w1.open();
      w1.addToDocument();

      function _genericListUpdater(url,combobox)
      {
        var g=new qx.io.remote.Request(url,"GET","application/json");
        g.addEventListener("completed", function(e) {
          qx.log.Logger.ROOT_LOGGER.debug("AJAX call completed: "+url);
          combobox.setEnabled(false);
          combobox.getList().removeAll();
          r=e.getContent().items;
          for(var i = 0 ; i < r.length ; i++) // does not work in IE with "for (i in r)"
          {
            //var label = r[i][0];
            //var id = r[i][1];
            combobox.add(new qx.ui.form.ListItem(r[i][0], null, r[i][1]));
          }
          combobox.setSelected(null);
          combobox.setEnabled(true);
        });
        g.send();
      }

      function _updateServerGroupList()
      {
        _genericListUpdater(urls.maingroups,combo1);
        combo2.getList().removeAll();
        combo2.setSelected(null);
        combo3.getList().removeAll();
        combo3.setSelected(null);
        combo4.getList().removeAll();
        combo4.setSelected(null);
        combo5.getList().removeAll();
        combo5.setSelected(null);
        b3.setEnabled(false);
        b5.setEnabled(false);
        r2.setEnabled(false);
        r3.setEnabled(false);
        r4.setEnabled(false);
        r5.setEnabled(false);
      }
      function _updateHostGroupList(maingroupid)
      {
        _genericListUpdater(urls.hostgroups+"?maingroupid="+maingroupid,combo2);
        combo3.getList().removeAll();
        combo3.setSelected(null);
        combo4.getList().removeAll();
        combo4.setSelected(null);
        combo5.getList().removeAll();
        combo5.setSelected(null);
        b3.setEnabled(false);
        b5.setEnabled(false);
        r2.setEnabled(true);
        r3.setEnabled(false);
        r4.setEnabled(false);
        r5.setEnabled(false);
      }
      function _updateHostList(othergroupid)
      {
        _genericListUpdater(urls.hosts+"?othergroupid="+othergroupid,combo3);
        combo4.getList().removeAll();
        combo4.setSelected(null);
        combo5.getList().removeAll();
        combo5.setSelected(null);
        b3.setEnabled(false);
        b5.setEnabled(false);
        r3.setEnabled(true);
        r4.setEnabled(false);
        r5.setEnabled(false);
      }
      function _updateGraphGroupList(idhost)
      {
        _genericListUpdater(urls.graphgroups+"?idhost="+idhost,combo4);
        combo5.getList().removeAll();
        combo5.setSelected(null);
        r4.setEnabled(true);
        r5.setEnabled(false);
        b5.setEnabled(false);
      }
      function _updateGraphList(idservice)
      {
        _genericListUpdater(urls.graphs+"?idservice="+idservice,combo5);
        r5.setEnabled(true);
        b5.setEnabled(false);
      }
      combo1.addEventListener("changeSelected", function(e) { if(e.getValue()) _updateHostGroupList(e.getValue().getValue()); });
      combo2.addEventListener("changeSelected", function(e) { if(e.getValue()) _updateHostList(e.getValue().getValue()); });
      combo3.addEventListener("changeSelected", function(e) { if(e.getValue()) { b3.setEnabled(true);_updateGraphGroupList(e.getValue().getValue());} });
      combo4.addEventListener("changeSelected", function(e) { if(e.getValue()) { _updateGraphList(e.getValue().getValue());} });
      //combo4.addEventListener("changeSelected", function(e) { if(e.getValue()) { _updateGraphList(combo3.getSelected().getLabel(),e.getValue().getLabel());} });
      combo5.addEventListener("changeSelected", function(e) { if(e.getValue()) b5.setEnabled(true); });

      r1.addEventListener("execute",function(e) { _updateServerGroupList();});
      r2.addEventListener("execute",function(e) { _updateHostGroupList(combo1.getSelected().getLabel());});
      r3.addEventListener("execute",function(e) { _updateHostList(combo2.getSelected().getLabel());});
      r4.addEventListener("execute",function(e) { _updateGraphGroupList(combo3.getSelected().getLabel());});
      r5.addEventListener("execute",function(e) { _updateGraphList(combo3.getSelected().getLabel(),combo4.getSelected().getLabel());});
      // Restore previously opened windows
      var state = qx.client.History.getInstance().getState();
      qx.log.Logger.ROOT_LOGGER.debug("state: "+state);
      if (state != "") {
        var windows;
        if (state.match(/\+/)) { // More than one windows opened
          windows = state.split(/\+/);
        } else {
          windows = new Array(state);
        }
        for (var i=0, l=windows.length; i<l; i++) {
          var item = windows[i];
          if (!item.match(/;/)) { qx.log.Logger.ROOT_LOGGER.debug("skipping graph: "+item); continue; }
          var item_a = item.split(/;/);
          var host, graph, left, top;
          host = item_a[0];
          graph = decodeURIComponent(item_a[1]);
          wleft = item_a[2];
          wtop = item_a[3];
          qx.log.Logger.ROOT_LOGGER.debug("restoring graph: "+host+";"+graph+";"+wleft+";"+wtop);
          this.openGraph(host, graph, wleft, wtop, false);
        }
      }
    },


    /**
     * Graph-opening function
     *
     * @type member
     */

    openGraph: function(host, graph, wleft, wtop, add_to_history)
    {
      //  position - sauvegarde valeurs courantes
      var wleft_c = wleft;
      var wtop_c = wtop;

      var url;
      var start;
      var duration;
      var fakeIncr=0;
      // Create UI elements
      var w=new qx.ui.window.Window(this.tr("\"%1\" Graph for host %2", graph, host), "icon/16/apps/accessories-time-tracking.png");
      var l=new qx.ui.layout.FlowLayout;
      l.set({"paddingTop": 26 });
      var l2=new qx.ui.layout.HorizontalBoxLayout;
      var bt_refresh=new qx.ui.form.Button("","icon/16/actions/view-refresh.png");
      bt_refresh.setToolTip(new qx.ui.popup.ToolTip(this.tr("Reload graph")));
      bt_refresh.setBorder("outset");
      // Timeframe menu
      var time_menu = new qx.ui.menu.Menu();
      var timeframes = [ 
        [12, this.tr("Last 12 hours")],
        [24, this.tr("Last 24 hours")],
        [48, this.tr("Last 48 hours")],
        [7*24, this.tr("Last 7 days")],
        [14*24, this.tr("Last 14 days")],
        [3*31*24, this.tr("Last 3 months")],
        [183*24, this.tr("Last 6 months")],
        [365*24, this.tr("Last year")]
      ];
      for (var i = 0, item; item = timeframes[i]; i++) {
          var menu_bt = new qx.ui.menu.Button(item[1]);
          menu_bt.title = item[0]
          menu_bt.addEventListener("execute",function(e) { setTail(this.title); });
          time_menu.add(menu_bt);
      }
      time_menu.addToDocument();
      var time_menu_bt = new qx.ui.form.Button(this.tr("Timeframe"),"icon/16/actions/history.png");
      time_menu_bt.setToolTip(new qx.ui.popup.ToolTip(this.tr("Timeframe menu")));
      // Browse buttons
      var bt_first=new qx.ui.form.Button("","icon/16/actions/start.png");
      bt_first.setToolTip(new qx.ui.popup.ToolTip(this.tr("Graph start")));
      var bt_prev=new qx.ui.form.Button("","icon/16/actions/go-previous.png");
      bt_prev.setToolTip(new qx.ui.popup.ToolTip(this.tr("Last section")));
      var bt_next=new qx.ui.form.Button("","icon/16/actions/go-next.png");
      bt_next.setToolTip(new qx.ui.popup.ToolTip(this.tr("Next section")));
      var bt_last=new qx.ui.form.Button("","icon/16/actions/dialog-finish.png");
      bt_last.setToolTip(new qx.ui.popup.ToolTip(this.tr("Graph end")));
      var bt_zoomin=new qx.ui.form.Button("","icon/16/actions/zoom-in.png");
      bt_zoomin.setToolTip(new qx.ui.popup.ToolTip(this.tr("Zoom in")));
      var bt_zoomout=new qx.ui.form.Button("","icon/16/actions/zoom-out.png");
      bt_zoomout.setToolTip(new qx.ui.popup.ToolTip(this.tr("Zoom out")));
      var h1=new qx.ui.layout.HorizontalBoxLayout;

      // Export Menu
      var indicator_menu = new qx.ui.menu.Menu();
      indicator_menu.addToDocument();
      var indicator_menu_bt = new qx.ui.form.Button(this.tr("Export CSV"),"icon/16/actions/document-export.png");
      indicator_menu_bt.setToolTip(new qx.ui.popup.ToolTip(this.tr("Export CSV")));

      w.setDimension("auto", "auto");
      w.setShowMinimize(false);
      w.setShowMaximize(false);
      w.setResizable(false, false, false, false);

      function setUrl(start,duration)
      {
        url= urls.getImage+"?host="+encodeURIComponent(host)+"&start="+start+"&duration="+duration+"&graph="+encodeURIComponent(graph);
        qx.log.Logger.ROOT_LOGGER.debug(url);
      }
      function loadImage(myUrl,o)
      {
        o.removeAll();
        var i=new qx.io.remote.Request(url,"GET","text/plain");
        i.addEventListener("completed", function(e) { 
          img = e.getContent();
          if (img)
          {
            o.add(new qx.ui.basic.Image(e.getContent()));
          }
        });
        i.send();
      }
      function getTime() // we use a function because the window can be opened a long time without reloading
      {
        var now_obj = new Date();
        return parseInt(now_obj.getTime() / 1000);
      }
      function updateGraphOnStartTime()
      {
        var url= urls.getStartTime+"?host="+encodeURIComponent(host);
        var g=new qx.io.remote.Request(url,"GET","text/plain");
        g.addEventListener("completed", function(e) { 
          start = parseInt(e.getContent());
          setStep(start);
          bt_first.setEnabled(false); 
          bt_prev.setEnabled(false);
        });
        g.send();
      }
      function getIndexWindow (cdi, w)
      {
        // var cdi = qx.ui.core.ClientDocument.getInstance();
        var index_l = -1;
        if (cdi)
        {
          var nb = cdi.getChildren().length;
          for (i = 0; i < nb; i++)
          {
            var c_l = cdi.getChildren()[i];
            if (c_l)
            {
              if (c_l.name == "qx.ui.window.Window")
              {
                caption_l = c_l.getCaption();
                if (c_l == w)
                {
                  index_l = i;
                }
              }
            }
          }
        }
        return index_l;
      }

      // timer pour rafraichissement
      var delay = 5*60*1000;
      var t = undefined;
      function tempoFireRefresh()
      {
        t = setTimeout(tempoFallRefresh, delay);
      }
      function tempoFallRefresh()
      {
        var now = getTime();
        start = now - 24 * 3600;
        duration = 24 * 3600;
        setUrl(start, duration);
        loadImage(url,l);
        // rafraichissement periodique
        tempoFireRefresh();
      }
      function tempoClearRefresh()
      {
        if (t != undefined)
        {
          clearTimeout(t);
        }
      }
      function tempoDelayRefresh()
      {
        var url= urls.tempoDelayRefresh;
        var r = new qx.io.remote.Request(url,"GET","text/plain");
        r.addEventListener("completed", function(e) { 
          delay = e.getContent();
        });
        r.send();
      }
      function getIndicators(graph)
      {
        var url= urls.getIndicators+"?graph="+graph;
        var r = new qx.io.remote.Request(url,"GET","application/json");
        r.addEventListener("completed", function(e) { 
          r = e.getContent().items;
          var txt = "";
          for(var i = 0; i <= r.length; i++)
          {
            txt = "All";
            if (i < r.length)
            {
              txt = r[i][0];
            }
            var menu_bt = new qx.ui.menu.Button(txt);
            menu_bt.title = txt
            menu_bt.addEventListener("execute",function(e) { getExport(this.title); });
            indicator_menu.add(menu_bt);
          }
        });
        r.send();
      }

      // Default
      var now = getTime();
      start = now - 24 * 3600;
      duration = 24 * 3600;
      setUrl(start, duration);
      loadImage(url,l);
      getIndicators(graph);

      // Events
      tempoDelayRefresh();
      bt_refresh.addEventListener("execute",function(e) {
        var state = "activated";
        if (bt_refresh.hasState(state))
        {
          // bouton actif -> on le rend desactif
          bt_refresh.setBorder("outset");
          bt_refresh.removeState(state);
          // liberation timer
          tempoClearRefresh();
        }
        else
        {
          // bouton desactif -> on le rend actif
          bt_refresh.setBorder("inset");
          bt_refresh.addState(state);
          loadImage(url,l);
          // armement timer pour rafraichissement periodique
          tempoFireRefresh();
        }
      });

      time_menu_bt.addEventListener("click", function(e)
      {
        if ( time_menu.isSeeable() )
        {
          time_menu.hide();
        }
        else
        {
          var el = this.getElement();
          time_menu.setLeft(qx.html.Location.getPageBoxLeft(el));
          time_menu.setTop(qx.html.Location.getPageBoxBottom(el));
          time_menu.show();
        }
        e.setPropagationStopped(true);
      });
      time_menu_bt.addEventListener("mousedown", function(e) { e.setPropagationStopped(true); });

      function setTail(hours)
      {
        now = getTime();
        start=now-hours*3600; 
        duration=hours*3600; 

        setUrl(start,duration);
        loadImage(url,l);
        bt_first.setEnabled(true);
        bt_prev.setEnabled(true);
        bt_zoomin.setEnabled(true);
        bt_zoomout.setEnabled(true);
      }
      function setStep(start_ts)
      {
        start = start_ts;
        setUrl(start, duration);

        loadImage(url,l);
        bt_first.setEnabled(true);
        bt_prev.setEnabled(true);
        bt_next.setEnabled(true);
        bt_last.setEnabled(true);
        bt_zoomin.setEnabled(true);
        bt_zoomout.setEnabled(true);
      }

      bt_first.addEventListener("execute", function(e) { updateGraphOnStartTime() });
      bt_prev.addEventListener("execute", function(e) { setStep(start-duration); });
      bt_next.addEventListener("execute", function(e) { setStep(start+duration); });
      bt_last.addEventListener("execute", function(e) { 
        now = getTime(); 
        setStep(now-duration); 
      });
      bt_zoomin.addEventListener("execute", function(e) { duration = duration / 2; setStep(start+duration/2); });
      bt_zoomout.addEventListener("execute", function(e) { 
        start = start - duration / 2; 
        duration = duration * 2; 
        setStep(start); 
      });

      indicator_menu_bt.addEventListener("click", function(e)
      {
        if ( indicator_menu.isSeeable() )
        {
          indicator_menu.hide();
        }
        else
        {
          var el = this.getElement();
          indicator_menu.setLeft(qx.html.Location.getPageBoxLeft(el));
          indicator_menu.setTop(qx.html.Location.getPageBoxBottom(el));
          indicator_menu.show();
        }
        e.setPropagationStopped(true);
      });
      indicator_menu_bt.addEventListener("mousedown", function(e) { e.setPropagationStopped(true); });

      function getExport(indicator)
      {
        if (indicator != "")
        {
          var end = start + duration;
          var url= urls.exportCSV+"?host="+encodeURIComponent(host)+"&graph="+graph+"&indicator="+indicator+"&start="+start+"&end="+end;
          var w3 = window.open(url);
        }
      }

      // Setup the UI
      h1.add(bt_refresh);
      h1.add(time_menu_bt);
      h1.add(bt_first);
      h1.add(bt_prev);
      h1.add(bt_next);
      h1.add(bt_last);
      h1.add(bt_zoomin);
      h1.add(bt_zoomout);
      h1.add(indicator_menu_bt);
      h1.pack();
      l2.add(l);
      l2.add(h1);
      w.add(l2);

      w.addEventListener("appear", function(e) {
        wleft_c = this.getLeft();
        wtop_c = this.getTop();
      });

      w.addEventListener("disappear", function(e) {
        var state = qx.client.History.getInstance().getState();

        // parametres courants
        var cp = host+";"+encodeURIComponent(graph)+";"+wleft_c+";"+wtop_c+"+";
        var pos = state.indexOf(cp);
        if (pos >= 0)
        {
          // actualisation etat
          var state = state.replace(cp, "");
          qx.client.History.getInstance().addToHistory(state, this.tr("Vigilo Graphic"));
        }

        // pour rafraichissement
        var index_l = -1;
        var cdi = qx.ui.core.ClientDocument.getInstance();
        index_l = getIndexWindow(cdi, w);
        if (index_l != -1)
        {
          // suppression element courant
          c_l = cdi.getChildren()[index_l];
          cdi.remove(c_l);
        }
      });
      w._captionBar.addEventListener("mouseup", function(e) { 
        var state = qx.client.History.getInstance().getState();

        var wleft = this.getLeft();
        var wtop = this.getTop();

        // parametres courants et actuels
        var cp = host+";"+encodeURIComponent(graph)+";"+wleft_c+";"+wtop_c+"+";
        var ap = host+";"+encodeURIComponent(graph)+";"+wleft+";"+wtop+"+";

        var pos = state.indexOf(cp);
        if (pos >= 0)
        {
          // actualisation etat
          var state = state.replace(cp, ap);
          qx.client.History.getInstance().addToHistory(state, this.tr("Vigilo Graphic"));
          wleft_c = wleft;
          wtop_c = wtop;
        }
      }, w);
      w.addToDocument();
      w.open();
      wleft = parseInt(wleft);
      wtop = parseInt(wtop);
      if (wleft) { 
        w.setLeft(wleft); 
      } else {
        // w.setRight() makes the close button fixed on the page even if you move the window
        w.setLeft(qx.ui.core.ClientDocument.getInstance().getClientWidth() - 600);
      }
      if (wtop) { 
        w.setTop(wtop); 
      } else {
        w.setTop(5);
      }

      // Add to history if we are opening a new window (not on restore)
      if (add_to_history) {
        var state = qx.client.History.getInstance().getState();
        var wleft = w.getLeft();
        if (!wleft) { wleft = 0; }
        var wtop = w.getTop();
        if (!wtop) { wtop = 0; }
        state += host+";"+encodeURIComponent(graph)+";"+wleft+";"+wtop+"+";
        qx.client.History.getInstance().addToHistory(state, this.tr("Vigilo Graphic"));
        qx.log.Logger.ROOT_LOGGER.debug("state: "+state);
      }
    },
    
	
    /**
     * On window close (verbatim from qooxdoo's skeleton)
     *
     * @type member
     */
    close : function()
    {
      this.base(arguments);

      // Prompt user
      // return "Do you really want to close the application?";
    },


    /**
     * Destructor (verbatim from qooxdoo's skeleton)
     *
     * @type member
     */
    terminate : function() {
      this.base(arguments);
    }
  },




  /*
  *****************************************************************************
     SETTINGS
  *****************************************************************************
  */

  settings : {
    "vigigraph.resourceUri" : "./resource"
  }
});


// vim: set tabstop=2 shiftwidth=2 expandtab :
