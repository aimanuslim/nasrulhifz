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
        console.log($('input[name=mode-select]:checked', '#reviseParameters').attr('id'))
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




})