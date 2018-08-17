var idx = 1
function cloneMore(selector, type) {
    var newElement = $(selector).clone(true);
    var total = $('#id_' + type + '-TOTAL_FORMS').val();
    newElement.find(':input:not(:button)').each(function() {
        var name = $(this).attr('name').replace('-' + (total-1) + '-','-' + total + '-');
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
    });
    newElement.find('label').each(function() {
        var newFor = $(this).attr('for').replace('-' + (total-1) + '-','-' + total + '-');
        $(this).attr('for', newFor);
    });
    total++;
    $('#id_' + type + '-TOTAL_FORMS').val(total);
    $(selector).after(newElement);
}

function deleteForm(prefix, btn) {
    var total = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    if (total > 1){
    	btn.parent().parent().remove();
        $('#id_' + prefix + '-TOTAL_FORMS').val(total-1);
    }

    return false;
}

$(document).ready(function(){

    $("#submit-button").click(function(){
        $this.parent().attr('method') = "POST"
    });
	
	$(".add").click(function() {
		// console.log("Here")
		// var newDiv = $("form > div:nth-child(4)").clone(true)
		// var numOfFormChild = $("form").children.length - 1;
		// // newDiv.children('div').children('.input-group').children('input').attr('name', 'index-' + idx)
		// newDiv.insertBefore(".append");
		cloneMore('.input-group:last', 'form');

		idx += 1;

		return false;
	});

	$(".remove").click(function() {
		deleteForm('form', $(this));
		return false;

	});



})