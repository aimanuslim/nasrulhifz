
$(document).on('click', '.table-success', function() {
		$(this).removeClass("table-success").addClass("table-primary")
		$(this).children(':input').val("2")
	});

$(document).on('click', '.table-primary', function() {
		$(this).removeClass("table-primary").addClass("table-danger")
		$(this).children(':input').val("1")
	});

$(document).on('click', '.table-danger', function() {
		$(this).removeClass("table-danger").addClass("table-success")
		$(this).children(':input').val("3")
	});


// $(document).ready(function(){
// 	$(".table-success").click(function() {
// 		$(this).removeClass("table-success").addClass("table-primary")
// 	});


// 	$(".table-primary").click(function() {
// 		$(this).removeClass("table-primary").addClass("table-danger")
// 	});

// 	$(".table-danger").click(function() {
// 		$(this).removeClass("table-danger").addClass("table-success")
// 	});
// })
