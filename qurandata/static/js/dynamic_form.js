var idx = 1

var showingLimit = false
var wordShown = false

$(document).ready(function(){



    $("#limit-button").click(function(){
        if(showingLimit){
            $('#ayat-mode-input').val('ayat_number')
            $('#limit-forms').hide();
            $('#ayat-number-input').show();
            $("#limit-button").text('Enter limits')
            showingLimit = false
        } else{
            $('#ayat-mode-input').val('ayat_limit')
            $('#limit-forms').show();
            $('#ayat-number-input').hide();
            $("#limit-button").text('Enter ayat')
            showingLimit = true
        }
    });

    $('#reviseParameters input').on('change', function(){
        if($('input[name=mode-select]:checked', '#reviseParameters').attr('id') == 'surah_mode'){
            $('#unit-number').attr('placeholder', "Surah Number")
        }

        if($('input[name=mode-select]:checked', '#reviseParameters').attr('id') == 'juz_mode'){
            $('#unit-number').attr('placeholder', "Juz Number")
        }
    })

    $("#show-ayat-button").click(function(){
        if(wordShown){
            $(".hidden-word").hide();
            $(".blank-lines").show();
            $(this).text('Show Words')
            wordShown = false
        } else {
            $(".hidden-word").show();
            $(".blank-lines").hide();
            $(this).text('Hide Words')
            wordShown = true
        }

    })

    $('#surah-number-form').focusout(function(){
        var surah_number = $(this).val()
        console.log(surah_number)
        $.get("", {'surah_number': surah_number, 'change_limits': 'true'}, function(data){
            console.log(data)
            $('#ayat-number-input').attr('max', data['surah_limit'])
        })

    });

    $(".custom-carousel-button").click(function(){
        var refreshedForm = $('#refreshed-checkbox-form')
        var surah_number = $('.active #surah-number').text()
        var ayat_number = $('.active #ayat-number').text()
//        console.log(surah_number)
//        console.log(ayat_number)
        var isChecked = $("#refreshed-checkbox").is(':checked')

        var token =  $('input[name="csrfmiddlewaretoken"]').attr('value')
        var data = {}
        data['surah_number'] = surah_number
        data['ayat_number'] = ayat_number
        data['hifz_was_refreshed'] = isChecked
        data['csrfmiddlewaretoken'] = token

        // Send the data using post
        var posting = $.post( refreshedForm.attr('action'), data );

        // if success:
        posting.done(function(data) {
            // success actions, maybe change submit button to 'friend added' or whatever
        });
        // if failure:
        posting.fail(function(data) {
            // 4xx or 5xx response, alert user about failure
        });

        $("#refreshed-checkbox").prop('checked', false)
    });







})
