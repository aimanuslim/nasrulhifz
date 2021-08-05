var idx = 1

var showingLimit = false
var wordShown = false
var clueShown = false

$(document).ready(function(){



    $("#limit-button").click(function(){
        if(showingLimit){
            $('#ayat-mode-input').val('ayat_number')
            $('#limit-forms').hide();

            $('#min-limit-input').val('');
            $('#max-limit-input').val('');

            $('#ayat-number-input').show();
            $("#limit-button").text('Enter limits')
            $('#display-button').show()
            showingLimit = false
        } else{
            $('#ayat-mode-input').val('ayat_limit')
            $('#limit-forms').show();
            $('#ayat-number-input').hide();
            $('#display-button').hide()

            $('#ayat-number-input').val('');

            $("#limit-button").text('Enter ayat')
            showingLimit = true
        }
    });

    $('#reviseParameters input').on('change', function(){
        if($('input[name=mode-select]:checked', '#reviseParameters').attr('id') == 'surah_mode'){
            $('#unit-number').attr('disabled', false)
            $('#unit-number').attr('placeholder', "Surah Number")
            $('#unit-number').attr('max', "114")
        }

        if($('input[name=mode-select]:checked', '#reviseParameters').attr('id') == 'juz_mode'){
            $('#unit-number').attr('disabled', false)
            $('#unit-number').attr('placeholder', "Juz Number")
            $('#unit-number').attr('max', "30")
        }

        if($('input[name=mode-select]:checked', '#reviseParameters').attr('id') == 'free_mode'){
            $('#unit-number').attr('disabled', true)
        }
    })



    $("#show-clue-button").click(function(){
        if(clueShown){
            $(".clue-word").hide();
            $(".clue-blank-lines").show();
            $(this).text('Show Clue')
            clueShown = false
        } else {
            $(".clue-word").show();
            $(".clue-blank-lines").hide();
            $(this).text('Hide Clue')
            clueShown = true
        }

    })

    $('#surah-number-form').focusout(function(){
        var surah_number = $(this).val()
//        console.log(surah_number)
        $.get("", {'surah_number': surah_number, 'change_limits': 'true'}, function(data){
//            console.log(data)
            $('#ayat-number-input').attr('max', data['surah_limit'])
            $('#min-limit-input').attr('max', data['surah_limit'])
            $('#max-limit-input').attr('max', data['surah_limit'])
        })

    });

    $('.surah-param-inputs').focusout(function(){
        $('.mydiv').remove()
        $('#submit-button').text('Submit')
    })

    $('#close-display').click(function(){
        $('.mydiv').remove()
        $('#submit-button').text('Submit')
    })

    $(".custom-carousel-button").click(function(){
        var refreshedForm = $('#refreshed-checkbox-form')
        var surah_number = $('.active #surah-number').text()
        var ayat_number = []
        $(".active .hidden-ayat").each(function(index){
            ayat_number.push($(this).text())
//            console.log('Hidden ayat is:' + $(this).text())
        });
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

function GoBackWithRefresh(event) {
    if ('referrer' in document) {
        window.location = document.referrer;
        /* OR */
        //location.replace(document.referrer);
    } else {
        window.history.back();
    }
}