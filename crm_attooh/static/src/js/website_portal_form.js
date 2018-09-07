odoo.define('website_attooh_form.animation', function (require) {
'use strict';

    var core = require('web.core');
    var time = require('web.time');
    var ajax = require('web.ajax');
    var sAnimation = require('website.content.snippets.animation');

    var _t = core._t;
    var qweb = core.qweb;

    
    sAnimation.registry.form_builder_send = sAnimation.Class.extend({
        selector: '.s_website_attooh_form',

        willStart: function () {
            var def;
            if (!$.fn.datetimepicker) {
                def = ajax.loadJS("/web/static/lib/bootstrap-datetimepicker/src/js/bootstrap-datetimepicker.js");
            }
            return $.when(this._super.apply(this, arguments), def);
        },

        start: function (editable_mode) {
            if (editable_mode) {
                this.stop();
                return;
            }
            var self = this;
            this.templates_loaded = ajax.loadXML('/website_form/static/src/xml/website_form.xml', qweb);
            this.$target.find('.o_website_form_send').on('click',function (e) {self.send(e);});
            this.$target.find('.delete').on('click', function (e) {
                self.delete(e);
            });
            this.$target.find('.add_line').on('click',function (e) {self.add_line(e);});
            // this.$target.validator();

            // Initialize datetimepickers
            var datepickers_options = {
                minDate: moment({ y: 1900 }),
                maxDate: moment().add(200, "y"),
                calendarWeeks: true,
                icons : {
                    time: 'fa fa-clock-o',
                    date: 'fa fa-calendar',
                    next: 'fa fa-chevron-right',
                    previous: 'fa fa-chevron-left',
                    up: 'fa fa-chevron-up',
                    down: 'fa fa-chevron-down',
                   },
                locale : moment.locale(),
                format : time.getLangDateFormat(),
            };
            
            datepickers_options.format = 'YYYY-MM-DD';
            this.datepickers_options = datepickers_options;
            this.$target.find('.o_website_form_date').datetimepicker(datepickers_options);

            return this._super.apply(this, arguments);
        },

        destroy: function () {
            this._super.apply(this, arguments);
            this.$target.find('button').off('click');
        },
        add_line: function (e) {
            e.preventDefault();
            var $tr_clone = this.$target.find('.clone_tr');
            var $tr = $tr_clone.clone(true).removeClass('clone_tr o_hidden');
            $tr.find("input[type!='hidden']").attr('required', 'required');
            $tr.insertAfter(this.$target.find('table tr:last'));
            
            // Initialize datetimepickers
            $tr.find('.o_website_form_date').removeData('DateTimePicker').datetimepicker(this.datepickers_options);
        },
        delete: function (e) {
            e.preventDefault();
            var id = $(e.currentTarget).data('id');
            if (id){
                var delete_ids = this.$target.data('delete_ids') || [];
                delete_ids.push(id);
                this.$target.data('delete_ids', delete_ids);
            }
            $(e.currentTarget).closest('tr').remove();
        },

        send: function (e) {
            e.preventDefault();  // Prevent the default submit behavior
            if (!this.$target.get(0).checkValidity()){
                this.$target.get(0).reportValidity();
                return;
            }
            
            // Prevent users from crazy clicking
            this.$target.find('.o_website_form_send').off().addClass('disabled');
            var self = this;
            self.$target.find('#o_website_form_result').empty();
            if (!self.check_error_fields({})) {
                self.update_status('invalid');
                return false;
            }

            this.$target.find('.clone_tr').remove();
            // Prepare form inputs
            this.form_fields = this.$target.serializeArray();
            _.each(this.$target.find('input[type=file]'), function (input) {
                $.each($(input).prop('files'), function (index, file) {
                    // Index field name as ajax won't accept arrays of files
                    // when aggregating multiple files into a single field value
                    self.form_fields.push({
                        name: input.name + '[' + index + ']',
                        value: file
                    });
                });
            });

            // Serialize form inputs into a single object
            // Aggregate multiple values into arrays
            var form_values = {};
            var force_action = this.$target.data('force_action');
            if (_.contains(['assets', 'liabilities', 'dependent', 'bugdet_income', 'bugdet_expense'], force_action)) {
                var values = [];
                form_values = [];
                var res = {};
                _.each(this.form_fields, function (field) {
                    var val = {};
                    if (values.length && field.name in _.last(values)) {
                        val[field.name] = field.value;
                        values.push(val);
                    } else if (values.length) {
                        _.last(values)[field.name] = field.value;
                    } else {
                        val[field.name] = field.value;
                        values.push(val);
                    }
                });
                res['to_update'] = values;
                res['to_delete'] = this.$target.data('delete_ids') || [];
                // res['to_create'] =
                form_values = {force_action : JSON.stringify(res)};
            } else {
                _.each(this.form_fields, function (input) {
                    if (input.name in form_values) {
                        // If a value already exists for this field,
                        // we are facing a x2many field, so we store
                        // the values in an array.
                        if (Array.isArray(form_values[input.name])) {
                            form_values[input.name].push(input.value);
                        } else {
                            form_values[input.name] = [form_values[input.name], input.value];
                        }
                    } else {
                        if (input.value !== '') {
                            form_values[input.name] = input.value;
                        }
                    }
                });
            }

            // Overwrite form_values array with values from the form tag
            // Necessary to handle field values generated server-side, since
            // using t-att- inside a snippet makes it non-editable !
            for (var key in this.$target.data()) {
                if (_.str.startsWith(key, 'form_field_')){
                    form_values[key.replace('form_field_', '')] = this.$target.data(key);
                }
            }

            // Post form and handle result
            ajax.post(this.$target.attr('action') + (this.$target.data('force_action')||this.$target.data('model_name')), form_values)
            .then(function (result_data) {
                result_data = $.parseJSON(result_data);
                if (!result_data.id) {
                    // Failure, the server didn't return the created record ID
                    self.update_status('error');
                    if (result_data.error_fields) {
                        // If the server return a list of bad fields, show these
                        // fields for users
                        self.check_error_fields(result_data.error_fields);
                    }
                } else {
                    // Success, redirect or update status
                    var success_page = self.$target.attr('data-success_page');
                    if (success_page) {
                        $(window.location).attr('href', success_page);
                    }
                    else {
                        self.update_status('success');
                    }

                    // Reset the form
                    self.$target[0].reset();
                }
            })
            .fail(function (result_data){
                self.update_status('error');
            });
        },

        check_error_fields: function (error_fields) {
            var self = this;
            var form_valid = true;
            // Loop on all fields
            this.$target.find('.form-field').each(function (k, field){
                var $field = $(field);
                var field_name = $field.find('.control-label').attr('for');

                // Validate inputs for this field
                var inputs = $field.find('.o_website_form_input:not(#editable_select)');
                var invalid_inputs = inputs.toArray().filter(function (input, k, inputs) {
                    // Special check for multiple required checkbox for same
                    // field as it seems checkValidity forces every required
                    // checkbox to be checked, instead of looking at other
                    // checkboxes with the same name and only requiring one
                    // of them to be checked.
                    if (input.required && input.type === 'checkbox') {
                        // Considering we are currently processing a single
                        // field, we can assume that all checkboxes in the
                        // inputs variable have the same name
                        var checkboxes = _.filter(inputs, function (input){
                            return input.required && input.type === 'checkbox';
                        });
                        return !_.any(checkboxes, function (checkbox) { return checkbox.checked; });

                    // Special cases for dates and datetimes
                    } else if ($(input).hasClass('o_website_form_date')) {
                        if (!self.is_datetime_valid(input.value, 'date')) {
                            return true;
                        }
                    } else if ($(input).hasClass('o_website_form_datetime')) {
                        if (!self.is_datetime_valid(input.value, 'datetime')) {
                            return true;
                        }
                    }
                    return !input.checkValidity();
                });

                // Update field color if invalid or erroneous
                $field.removeClass('has-error');
                if (invalid_inputs.length || error_fields[field_name]){
                    $field.addClass('has-error');
                    if (_.isString(error_fields[field_name])){
                        $field.popover({content: error_fields[field_name], trigger: 'hover', container: 'body', placement: 'top'});
                        // update error message and show it.
                        $field.data("bs.popover").options.content = error_fields[field_name];
                        $field.popover('show');
                    }
                    form_valid = false;
                }
            });
            return form_valid;
        },

        is_datetime_valid: function (value, type_of_date) {
            if (value === "") {
                return true;
            } else {
                try {
                    this.parse_date(value, type_of_date);
                    return true;
                } catch (e) {
                    return false;
                }
            }
        },

        // This is a stripped down version of format.js parse_value function
        parse_date: function (value, type_of_date, value_if_empty) {
            var date_pattern = time.getLangDateFormat(),
                time_pattern = time.getLangTimeFormat();
            var date_pattern_wo_zero = date_pattern.replace('MM','M').replace('DD','D'),
                time_pattern_wo_zero = time_pattern.replace('HH','H').replace('mm','m').replace('ss','s');
            switch (type_of_date) {
                case 'datetime':
                    var datetime = moment(value, [date_pattern + ' ' + time_pattern, date_pattern_wo_zero + ' ' + time_pattern_wo_zero], true);
                    if (datetime.isValid())
                        return time.datetime_to_str(datetime.toDate());
                    throw new Error(_.str.sprintf(_t("'%s' is not a correct datetime"), value));
                case 'date':
                    var date = moment(value, [date_pattern, date_pattern_wo_zero], true);
                    if (date.isValid())
                        return time.date_to_str(date.toDate());
                    throw new Error(_.str.sprintf(_t("'%s' is not a correct date"), value));
            }
            return value;
        },

        update_status: function (status) {
            var self = this;
            if (status !== 'success') {  // Restore send button behavior if
                                            // result is an error
                this.$target.find('.o_website_form_send').on('click',function (e) {self.send(e);}).removeClass('disabled');
            }
            var $result = this.$('#o_website_form_result');
            this.templates_loaded.done(function () {
                $result.replaceWith(qweb.render("website_form.status_" + status));
            });
        },
    });
    $(document).ready(function (){
        $('.button_preview').on('click',function (){
            $(this).parents('tr').find('#my_model').modal('show');
        });
        // TOFIX: on delete newly added line on finance personal portal
        // 'dropContainer' is undefined traceback

            // dropContainer.ondragover = dropContainer.ondragenter = function(evt) {
         //    evt.preventDefault();
         //  };
         // dropContainer.ondrop = function(evt) {
         //     doc_attachment.files = evt.dataTransfer.files;
         //   evt.preventDefault();
         // };
         $(document).on('click', '[data-toggle="lightbox"]', function (event) {
            event.preventDefault();
            $(this).ekkoLightbox();
        });

         setTimeout(function (){
             $('.media.o_portal_chatter_message .o_portal_chatter_attachments .col-md-2.col-sm-3.text-center').each(function (){
                 $(this).prepend("<button class='btn view_document_chatter' style='border: 1px solid steelblue;border-radius: 0;width: 95px;padding: 2px;margin-top: 10px;background: steelblue;color: white;'>View</button>");
             });
             
             $('.view_document_chatter').on('click',function (){
                $(document).find('#my_model_doc').remove();
                 var url = $(this).parents('.col-md-2.col-sm-3.text-center').find('a').attr('href');
                 var id= parseInt(url.split("content/")[1].split("?")[0]);
                 ajax.jsonRpc("/get_helpdesk_attachment_id", 'call', {'id': id})
                    .then(function (data) {
                        if (data.file_type === 'other'){
                            window.location.replace(data.src);
                        } else {
                            var html = "";
                            html += '<div id="my_model_doc" class="modal fade" role="dialog">';
                            html += '<div class="modal-header" style="border-bottom: unset;">';
                            html += '<span t-field="attachment.name" />';
                            html += '<h4 class="modal-title" style="color: white; float: left;">';
                            html += '</h4>';
                            html += '<button class="close" style="opacity: 1.0" type="button"';
                            html += 'data-dismiss="modal" aria-lable="Close">';
                            html += '<span aria-hidden="true" style="color: white;">x</span>';
                            html += '</button>';
                            html += '</div>';
                            html += '<div class="modal-dialog" style="width:80%;height:80%;">';
                            html += '<div class="modal-content" style="width:100%;height:100%;">';
                            html += '<div class="modal-body" style="width:100%;height:100%;padding:0px;">';
                            if (data.file_type === 'pdf'){
                                html += '<iframe class="mb48 o_viewer_pdf"';
                                html += 'src="'+data.src+'"';
                                html += 'style="width:100%;height:100%;" />';
                            } else {
                                html += '<img class="img-fluid" style="width:100%;"';
                                html += 'src="'+data.src+'" />';
                        }
                        html += '</div>';
                        html += '</div>';
                        html += '</div>';
                        html += '</div>';
                        $('body').append(html);
                        $('#my_model_doc').modal('show');
                       }
                    });
             });
        },500);
    });
});
