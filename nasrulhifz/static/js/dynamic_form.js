var idx = 1

var showingLimit = false
var wordShown = false
var clueShown = false

surah_data = {1: 7, 2: 286, 3: 200, 4: 176, 5: 120, 6: 165, 7: 206, 8: 75, 9: 129, 10: 109, 11: 123, 12: 111, 13: 43, 14: 52, 15: 99, 16: 128, 17: 111, 18: 110, 19: 98, 20: 135, 21: 112, 22: 78, 23: 118, 24: 64, 25: 77, 26: 227, 27: 93, 28: 88, 29: 69, 30: 60, 31: 34, 32: 30, 33: 73, 34: 54, 35: 45, 36: 83, 37: 182, 38: 88, 39: 75, 40: 85, 41: 54, 42: 53, 43: 89, 44: 59, 45: 37, 46: 35, 47: 38, 48: 29, 49: 18, 50: 45, 51: 60, 52: 49, 53: 62, 54: 55, 55: 78, 56: 96, 57: 29, 58: 22, 59: 24, 60: 13, 61: 14, 62: 11, 63: 11, 64: 18, 65: 12, 66: 12, 67: 30, 68: 52, 69: 52, 70: 44, 71: 28, 72: 28, 73: 20, 74: 56, 75: 40, 76: 31, 77: 50, 78: 40, 79: 46, 80: 42, 81: 29, 82: 19, 83: 36, 84: 25, 85: 22, 86: 17, 87: 19, 88: 26, 89: 30, 90: 20, 91: 15, 92: 21, 93: 11, 94: 8, 95: 8, 96: 19, 97: 5, 98: 8, 99: 8, 100: 11, 101: 11, 102: 8, 103: 3, 104: 9, 105: 5, 106: 4, 107: 7, 108: 3, 109: 6, 110: 3, 111: 5, 112: 4, 113: 5, 114: 6}


$(document).ready(function(){



    $("#limit-button").click(function(){
        if(showingLimit){
            $('#ayat-mode-input').val('ayat_number')
            $('#group-ayat').hide();
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
            $('#group-ayat').show();
            $('#ayat-number-input').hide();
            $('#display-button').hide()

            $('#ayat-number-input').val('');

            $("#limit-button").text('Enter ayat')
            showingLimit = true
        }
    });

    $('#reviseParameters input').on('change', function(){
        if($('input[name=mode-select]:checked', '#reviseParameters').attr('id') == 'surah_mode'){
            $('#unit-number').show()
            $('#unit-number').attr('placeholder', "Surah Number")
            $('#unit-number').attr('max', "114")
        }

        if($('input[name=mode-select]:checked', '#reviseParameters').attr('id') == 'juz_mode'){
            $('#unit-number').attr('disabled', false)
            $('#unit-number').attr('placeholder', "Juz Number")
            $('#unit-number').attr('max', "30")
        }

        if($('input[name=mode-select]:checked', '#reviseParameters').attr('id') == 'free_mode'){
            $('#unit-number').hide()
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
        $('#ayat-number-input').attr('max', surah_data[surah_number.toString()])
        $('#min-limit-input').attr('max', surah_data[surah_number.toString()])
        $('#max-limit-input').attr('max', surah_data[surah_number.toString()])

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