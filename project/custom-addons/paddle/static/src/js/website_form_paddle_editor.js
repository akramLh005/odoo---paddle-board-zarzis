odoo.define('paddle.form', function (require) {
'use strict';

var core = require('web.core');
var FormEditorRegistry = require('website.form_editor_registry');

const _lt = core._lt;

FormEditorRegistry.add('create_request', {
    formFields: [{
        type: 'char',
        modelRequired: true,
        fillWith: 'name',
        name: 'name',
        string: _lt('Name'),
    }, {
        type: 'tel',
        modelRequired: true,
        fillWith: 'phone',
        name: 'phone',
        string: _lt('Your Phone'),
    }, {
        type: 'integer',
        modelRequired: true,
        name: 'nbr_person',
        string: _lt('Number of Persons'),
    }],
    fields: [{
        name: 'date_id',
        type: 'many2one',
        relation: 'paddle.date',
        string: _lt('Date'),
        domain: [['is_available', '=', true], ['is_published', '=', true]],
        title: _lt('Date'),
    }, {
        name: 'session_id',
        type: 'many2one',
        relation: 'paddle.session',
        string: _lt('Session'),
        title: _lt('Session'),
    }],
});

});
