odoo.define('paddle.website_form', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');

    // Assuming these elements are used within the Odoo widget context
    var $allDivInfo = $(document.querySelectorAll(".s_website_form_rows > div"));
    var $available_days = $(document.querySelectorAll("#calendar .month_table div.o_slot_button"));
    var $date_id_class = $(document.querySelector(".date_id_class"));  // Assuming this holds the date ID
    var sections = document.querySelectorAll(".s_process_steps_connector_line i");

    $(document).ready(function() {
        $available_days.on('click', function(e, ctn) {
            var id = e.target.id;
            var lastThreeChars = id.slice(-5);  // Extract last 3 characters (assuming that's relevant)
            var $available_sessions = $(document.querySelectorAll(".o_slots_list > div"));
            var selectedSession;
            $(document.querySelector("#calendar")).hide(); // Assuming hide() is a jQuery method
            $(document.querySelector(".session_section")).removeClass("d-none"); // Assuming hide() is a jQuery method
            sections[0].classList.remove("bg-primary"); // Assuming hide() is a jQuery method
            sections[0].classList.add("bg-secondary"); // Assuming hide() is a jQuery method
            sections[1].classList.add("bg-primary"); // Assuming hide() is a jQuery method
            sections[1].classList.remove("bg-secondary"); // Assuming hide() is a jQuery method

            var optionDates = document.querySelectorAll("select[name='date_id'] option");
            for (let i = 0; i < optionDates.length; i++) {
                var test123 = optionDates[i].textContent.trim();
                if(id == test123) {
                    $(document.querySelector("select[name='date_id']")).val(optionDates[i].value);
                }
            }

            // Call RPC method (assuming you have a defined function)
            rpc.query({
                model: 'paddle.date',
                method: 'get_active_sessions',
                args: [id],  // Call with full ID
            }).then(function(result) {
                $available_sessions.each(function(element, content) {
                    for (let i = 0; i < result.length; i++) {
                        if(content.textContent == result[i].name) {
                            content.classList.remove('d-none');
                            content.classList.add('d-flex');
                            break;
                        }
                        content.classList.remove('d-flex');
                        content.classList.add('d-none');
                    }
                    const $form = $(document.querySelector("#hr_recruitment_form"));
                    var max_number = document.querySelector("#max_number");
                    var number_of_persons = document.querySelector("#nbr_person");

                    // Hide clicked session and show first $allDivInfo element
                    $(content).on('click', function() {
                        $(document.querySelector(".session_section")).addClass('d-none');
                        $allDivInfo.first().removeClass('d-none');  // Show first element
                        $allDivInfo.eq(1).removeClass('d-none');  // Show first element
                        $allDivInfo.eq(2).removeClass('d-none');  // Show first element
                        $allDivInfo.last().removeClass('d-none');  // Show first element
                        sections[1].classList.remove("bg-primary"); // Assuming hide() is a jQuery method
                        sections[1].classList.add("bg-secondary"); // Assuming hide() is a jQuery method
                        sections[2].classList.add("bg-primary"); // Assuming hide() is a jQuery method
                        sections[2].classList.remove("bg-secondary"); // Assuming hide() is a jQuery method
                        var optionSessions = document.querySelectorAll("select[name='session_id2'] option")
                        for (let i = 0; i < optionSessions.length; i++) {
                            var test = content.textContent.trim();
                            if(content.textContent == optionSessions[i].textContent.trim()) {
                                $(document.querySelector("select[name='session_id2']")).val(optionSessions[i].value)

                                // Call RPC method (assuming you have a defined function)
                                rpc.query({
                                    model: 'paddle.date',
                                    method: 'get_places_left',
                                    args: [id, optionSessions[i].value],  // Call with full ID
                                }).then(function(result) {
                                    max_number.textContent = "Max person: " + result[0]['max_number'];
                                    number_of_persons.setAttribute('max', result[0]['max_number']);
                                });
                            }
                        }
                    });

                });
            });
        });
    });
});
