odoo.define('website_crm_sign.utils', function (require) {
    'use strict';
    var ajax = require("web.ajax");
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var website_sign_utils = require('website_sign.utils');
    var framework = require('web.framework');
    var session = require('web.session');
    

    var _t = core._t;


    // var signTemplate = require("website_sign.template");
    function setAsOpportunitySelect($select) {
        var select2Options = {
            allowClear: true,
            multiple: $select.is('[multiple]'),
            minimumInputLength: 3,

            formatResult: function (opportunity, resultElem, searchObj) {
                return $("<div/>", {
                    text: opportunity.name
                }).addClass('o_sign_add_partner');
            },

            formatSelection: function (opportunity) {
                return $("<div/>", {
                    text: opportunity.name
                }).html();
            },

            ajax: {
                data: function (term, page) {
                    return {
                        'term': term,
                        'page': page
                    };
                },
                transport: function (args) {
                    var domain = _.chain(args.data.term.split(/[\s()]+/)).filter().map(function (term) {
                        return [
                            ['name', 'ilike', term],
                            ["type", "=", "opportunity"]
                        ];
                    }).flatten(true).value();
                    ajax.rpc('/web/dataset/call_kw', {
                        model: 'crm.lead',
                        method: 'search_read',
                        args: [domain, ['name']],
                        kwargs: {
                            limit: 30,
                            offset: 30 * (args.data.page - 1)
                        }
                    }).done(args.success).fail(args.failure);
                },
                results: function (data) {
                    var last_page = data.length !== 30;
                    // empty choice on last result page to create new partner
                    if (last_page) {
                        data.push({
                            'id': parseInt(_.uniqueId('-'))
                        });
                    }
                    _.each(data, function (partner) {
                        partner['name'] = partner['name'] || '';
                    });
                    return {
                        'results': data,
                        'more': !last_page
                    };
                },
                quietMillis: 250,
            }
        };
        $select.select2('destroy');
        $select.addClass('form-control');
        $select.select2(select2Options);
        // fix an issue select2 has to size a placeholder of an invisible input
        setTimeout(function () {
            $select.data('select2').clearSearch();
        });

        return {
            setAsOpportunitySelect: setAsOpportunitySelect,
        };
    }
    var Template = core.action_registry.get('website_sign.Template');

    var CreateSignatureRequestDialog = Dialog.extend({
            template: 'website_sign.create_signature_request_dialog',

            init: function(parent, templateID, rolesToChoose, templateName, attachment, options) {
                options = options || {};

                options.title = options.title || _t("Send Signature Request");
                options.size = options.size || "medium";

                options.buttons = (options.buttons || []);
                options.buttons.push({text: _t('Send'), classes: 'btn-primary', click: function(e) {
                    this.sendDocument();
                }});
                options.buttons.push({text: _t('Cancel'), classes: 'btn-default', close: true});

                this._super(parent, options);

                this.templateID = templateID;
                this.rolesToChoose = rolesToChoose;
                this.templateName = templateName;
                this.attachment = attachment;
            },

            willStart: function() {
                var self = this;
                return $.when(this._super(),
                    this._rpc({
                            model: 'res.users',
                            method: 'read',
                            args: [[session.uid], ['partner_id']],
                        })
                        .then(function(user) {
                            return self._rpc({
                                    model: 'res.partner',
                                    method: 'read',
                                    args: [[user[0].partner_id[0]], ['name']],
                                })
                                .then(prepare_reference);
                            })
                );

                function prepare_reference(partner) {
                    self.default_reference = "-";
                    var split = partner[0].name.split(' ');
                    for(var i = 0 ; i < split.length ; i++) {
                        self.default_reference += split[i][0];
                    }
                }
            },

            start: function() {
                this.$subjectInput = this.$('.o_sign_subject_input').first();
                this.$messageInput = this.$('.o_sign_message_textarea').first();
                this.$referenceInput = this.$('.o_sign_reference_input').first();

                this.$subjectInput.val('Signature Request - ' + this.templateName);
                var defaultRef = this.templateName + this.default_reference;
                this.$referenceInput.val(defaultRef).attr('placeholder', defaultRef);

                this.$('.o_sign_warning_message_no_field').first().toggle($.isEmptyObject(this.rolesToChoose));
                this.$('.o_sign_request_signers .o_sign_new_signer').remove();

                website_sign_utils.setAsPartnerSelect(this.$('.o_sign_request_signers .form-group input[type="hidden"]')); // Followers

                if($.isEmptyObject(this.rolesToChoose)) {
                    this.addSigner(0, _t("Signers"), true);
                } else {
                    var roleIDs = Object.keys(this.rolesToChoose).sort();
                    for(var i = 0 ; i < roleIDs.length ; i++) {
                        var roleID = roleIDs[i];
                        if(roleID !== 0)
                            this.addSigner(roleID, this.rolesToChoose[roleID], false);
                    }
                }

                this.addOpportunity();
                return this._super.apply(this, arguments);
                
            },
            addOpportunity: function () {
                var $oppotunity = this.$('#o_sign_crm_lead_select');
                setAsOpportunitySelect($oppotunity);
            },
            addSigner: function(roleID, roleName, multiple) {
                var $newSigner = $('<div/>').addClass('o_sign_new_signer form-group');

                $newSigner.append($('<label/>').addClass('col-md-3').text(roleName).data('role', roleID));

                var $signerInfo = $('<input type="hidden"/>').attr('placeholder', _t("Write email or search contact..."));
                if(multiple) {
                    $signerInfo.attr('multiple', 'multiple');
                }

                var $signerInfoDiv = $('<div/>').addClass('col-md-9');
                $signerInfoDiv.append($signerInfo);

                $newSigner.append($signerInfoDiv);

                website_sign_utils.setAsPartnerSelect($signerInfo);

                this.$('.o_sign_request_signers').first().prepend($newSigner);
            },

            sendDocument: function() {
                var self = this;

                var completedOk = true;
                self.$('.o_sign_new_signer').each(function(i, el) {
                    var $elem = $(el);
                    var partnerIDs = $elem.find('input[type="hidden"]').val();
                    if(!partnerIDs || partnerIDs.length <= 0) {
                        completedOk = false;
                        $elem.addClass('has-error');
                        $elem.one('focusin', function(e) {
                            $elem.removeClass('has-error');
                        });
                    }
                });
                if(!completedOk) {
                    return false;
                }

                var waitFor = [];

                var signers = [];
                self.$('.o_sign_new_signer').each(function(i, el) {
                    var $elem = $(el);
                    var selectDef = website_sign_utils.processPartnersSelection($elem.find('input[type="hidden"]')).then(function(partners) {
                        for(var p = 0 ; p < partners.length ; p++) {
                            signers.push({
                                'partner_id': partners[p],
                                'role': parseInt($elem.find('label').data('role'))
                            });
                        }
                    });
                    if(selectDef !== false) {
                        waitFor.push(selectDef);
                    }
                });

                var followers = [];
                var followerDef = website_sign_utils.processPartnersSelection(self.$('#o_sign_followers_select')).then(function(partners) {
                    followers = partners;
                });
                if(followerDef !== false) {
                    waitFor.push(followerDef);
                }

                var subject = self.$subjectInput.val() || self.$subjectInput.attr('placeholder');
                var reference = self.$referenceInput.val() || self.$referenceInput.attr('placeholder');
                var message = self.$messageInput.val();
                
                var opportunity_id = false;
                var opportunity_def  = website_sign_utils.processPartnersSelection(self.$('#o_sign_crm_lead_select')).then(function(opportunity) {
                    opportunity_id = opportunity.length ? opportunity[0] : false
                });
                if(opportunity_def !== false) {
                    waitFor.push(opportunity_def);
                }
                $.when.apply($, waitFor).then(function(result) {
                    self._rpc({
                            model: 'signature.request',
                            method: 'initialize_sign_new',
                            args: [self.templateID, signers, followers, opportunity_id, reference, subject, message],
                        })
                        .then(function(sr) {
                            self.do_notify(_t("Success"), _("Your signature request has been sent."));
                            self.do_action({
                                type: "ir.actions.client",
                                tag: 'website_sign.Document',
                                name: _t("New Document"),
                                context: {
                                    id: sr.id,
                                    token: sr.token,
                                    sign_token: sr.sign_token || null,
                                    create_uid: session.uid,
                                    state: 'sent',
                                },
                            });
                        }).always(function() {
                            self.close();
                        });
                });
            },
        });
    var ShareTemplateDialog = Dialog.extend({
        template: 'website_sign.share_template_dialog',

        events: {
            'focus input': function(e) {
                $(e.target).select();
            },
        },

        init: function(parent, templateID, options) {
            options = options || {};
            options.title = options.title || _t("Multiple Signature Requests");
            options.size = options.size || "medium";

            this.templateID = templateID;
            this._super(parent, options);
        },

        start: function() {
            var $linkInput = this.$('input').first();
            var linkStart = window.location.href.substr(0, window.location.href.indexOf('/web')) + '/sign/';

            return $.when(
                this._super(),
                this._rpc({
                        model: 'signature.request.template',
                        method: 'share',
                        args: [this.templateID],
                    })
                    .then(function(link) {
                        $linkInput.val((link)? (linkStart + link) : '');
                        $linkInput.parent().toggle(!!link).next().toggle(!link);
                    })
            );
        },
    });
    Template.include({
        init: function(parent, options) {
            this._super.apply(this, arguments);

            if(options.context.id === undefined) {
                return;
            }

            this.templateID = options.context.id;
            this.rolesToChoose = {};

            var self = this;
            var $sendButton = $('<button/>', {html: _t("Send"), type: "button"})
                .addClass('btn btn-primary btn-sm')
                .on('click', function() {
                    self.prepareTemplateData();
                    (new CreateSignatureRequestDialog(self, self.templateID, self.rolesToChoose, self.$templateNameInput.val(), self.signature_request_template.attachment_id)).open();
                });
            var $shareButton = $('<button/>', {html: _t("Share"), type: "button"})
                .addClass('btn btn-default btn-sm')
                .on('click', function() {
                    (new ShareTemplateDialog(self, self.templateID)).open();
                });
            this.cp_content = {$buttons: $sendButton.add($shareButton)};
        },
    });
});
