odoo.define('paddle.Dashboard', function(require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var web_client = require('web.web_client');
    var _t = core._t;
    var QWeb = core.qweb;
    var wamyProgramActivities = AbstractAction.extend({
        jsLibs: [
            '/web/static/lib/Chart/Chart.js',
        ],
        template: 'ProgramActivitiesBoard',
        events: {
            'click .click_all_programs': 'click_all_programs',
            'click .click_approved_programs': 'click_approved_programs',
            'click .click_canceled_programs': 'click_canceled_programs',
        },
        init: function(parent, context) {
            this._super(parent, context);
            this.dashboards_templates = ['wamyProgramActivities', 'RentingChart'];
            this.all_days = [];
            this.True_programs = [];
            this.False_programs = [];
            this.all_programs = [];
            this.in_progress = [];
            this.total_approved_programs = [];
            this.total_canceled_programs = [];
        },
        willStart: function() {
            var self = this;
            return this._super().then(function() {
                return self.fetch_data();
            });
        },
        start: function() {
            var self = this;
            this.set("title", 'Dashboard');
            return this._super().then(function() {
                self.render_dashboards();
                self.render_graphs();
            });
        },

        click_all_programs: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var options =
                self.do_action({
                    name: _t("All Programs"),
                    type: 'ir.actions.act_window',
                    res_model: 'paddle.board',
                    view_mode: 'tree,form,',
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    target: 'current',
                    context: {
                        'form_view_ref': 'paddle.paddle.board_form',
                        'tree_view_ref': 'paddle.view_paddle_board_tree',
                    },
                }, options)
        },
        click_approved_programs: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var options =
                self.do_action({
                    name: _t("Draft Programs"),
                    type: 'ir.actions.act_window',
                    res_model: 'paddle.board',
                    view_mode: 'tree,form,',
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    domain: [
                        ['state', '=', 'approved']
                    ],
                    target: 'current',
                    context: {
                        'form_view_ref': 'paddle.paddle.board_form',
                        'tree_view_ref': 'paddle.view_paddle_board_tree',
                    },
                }, options)
        },
        click_canceled_programs: function(e) {
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var options =
                self.do_action({
                    name: _t("Canceled Programs"),
                    type: 'ir.actions.act_window',
                    res_model: 'paddle.board',
                    view_mode: 'tree,form,',
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    domain: [
                        ['state', '=', 'canceled']
                    ],
                    target: 'current',
                    context: {
                        'form_view_ref': 'paddle.paddle.board_form',
                        'tree_view_ref': 'paddle.view_paddle_board_tree',
                    },
                }, options)

        },

        render_dashboards: function() {
            var self = this;
            _.each(this.dashboards_templates, function(template) {
                self.$('.o_renting_dashboard').append(QWeb.render(template, {
                    widget: self
                }));
            });
        },
        render_graphs: function() {
//            var self = this;
            this.get_contract_status();
            this.get_order_details();
        },

         get_contract_status: function () {

      var self = this
      var approved = _t('Approved');
      var canceled = _t('Canceled');
      var ctx = self.$(".top_renting_contract");
      rpc.query({
        model: "paddle.board",
        method: "get_contract_status",
      }).then(function (result) {
        var data = {
          labels: [approved, canceled],
          datasets: [
            {
              label: "",
              data: [result['approved_programs'], result['canceled_programs']],
              backgroundColor: [
                "#68A7AD",
                "#cd1313b3",
                "#cd1313b3",
                "#cd1313b3",
                "#cd1313b3",
                "#cd1313b3",
                "rgb(160, 150, 159)"
              ],
              borderColor: [
                "#E5CB9F",
                "rgb(69,129,142)",
                "rgba(75, 192, 192)",
                "rgb(100, 138, 163)",
                "#b5ded0",
                "#68A7AD",
                "rgb(160, 150, 159)"
              ],
              borderWidth: 0
            },
          ]
        };
        //options
        var options = {
          responsive: true,
          title: {
            display: true,
            position: "top",
            text: _t("Request Statistical"),
            fontSize: 18,
            fontColor: "#111",
            fontFamily: "'Almarai', sans-serif"
          },
          legend: {
            display: true,
            position: "bottom",
            labels: {
              fontColor: "#333",
              fontSize: 16,
              fontFamily: "'Almarai', sans-serif"
            }
          },
          scales: {
            xAxes: [{ gridLines: { display: false }, ticks: { display: false } }],
            yAxes: [{ gridLines: { display: false }, ticks: { display: false } }]
          },
        };
        //create Chart class object
        var chart = new Chart(ctx, {
          type: "pie",
          data: data,
          options: options
        });
      });
    },

         get_order_details: function () {

      var self = this
      var process = _t('Process');
      var finished = _t('Finish');
      var ctx = self.$(".top_renting_order");
      rpc.query({
        model: "paddle.date",
        method: "get_contract_status",
      }).then(function (result) {
        var data = {
          labels: [process, finished],
          datasets: [
            {
              label: "",
              data: [result['True_programs'], result['False_programs']],
              backgroundColor: [
                "#E5CB9F",
                "rgb(69,129,142)",
                "rgba(75, 192, 192)",
                "rgb(100, 138, 163)",
                "#b5ded0",
                "#68A7AD",
                "rgb(160, 150, 159)"
              ],
              borderColor: [
                "#E5CB9F",
                "rgb(69,129,142)",
                "rgba(75, 192, 192)",
                "rgb(100, 138, 163)",
                "#b5ded0",
                "#68A7AD",
                "rgb(160, 150, 159)"
              ],
              borderWidth: 1
            },
          ]
        };
        //options
        var options = {
          responsive: true,
          title: {
            display: true,
            position: "top",
            text: _t("Days Statistical"),
            fontSize: 18,
            fontColor: "#111",
            fontFamily: "'Almarai', sans-serif"
          },
          legend: {
            display: true,
            position: "bottom",
            labels: {
              fontColor: "#333",
              fontSize: 16,
              fontFamily: "'Almarai', sans-serif"
            }
          },
          scales: {
            xAxes: [{ gridLines: { display: false }, ticks: { display: false } }],
            yAxes: [{ gridLines: { display: false }, ticks: { display: false } }]
          },
        };
        //create Chart class object
        var chart = new Chart(ctx, {
          type: "pie",
          data: data,
          options: options
        });
      });
    },


        fetch_data: function() {
            var self = this;
            var defAll = this._rpc({
                model: 'paddle.board',
                method: 'get_contract_status'
            }).then(function(result) {
                self.all_days = result['all_days']
                self.True_programs = result['True_programs']
                self.False_programs = result['False_programs']
                self.all_programs = result['all_programs']
                self.in_progress = result['in_progress_programs']
                self.total_approved_programs = result['approved_programs']
                self.total_canceled_programs = result['canceled_programs']
            });
            return $.when(defAll);

        },
    });
    core.action_registry.add('wamyProgramActivities', wamyProgramActivities);
    return wamyProgramActivities;
});