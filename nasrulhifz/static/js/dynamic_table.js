
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


jQuery(document).ready(function($) {
    $(".clickable-row").click(function() {
        window.location = $(this).data("href");
    });
    $("#ayat-list-table").tablesorter();


});



function selectAll() {
    var checkboxes = document.getElementsByName('ayat_number');
    var selectAllBtn = document.getElementById('select-all-btn');
    var checked = false;
    for (var i = 0; i < checkboxes.length; i++) {
        checkboxes[i].checked = !checkboxes[i].checked;
        checked |= checkboxes[i].checked;
    }
    if (checked) {
        selectAllBtn.textContent = 'Deselect All';
    } else {
        selectAllBtn.textContent = 'Select All';
    }
    return false;
}


function filterTable() {
  // Declare variables
  var input, filter, table, tr, td, i, present;
  input = document.getElementById("filter-input");
  filter = input.value.toUpperCase();
  table = document.getElementById("ayat-list-table");
  tr = table.getElementsByTagName("tr");

  // Loop through all table rows, and hide those who don't match the search query
  for (i = 0; i < tr.length; i++) {
    alltd = tr[i].getElementsByTagName("td");
    present = false
    for(j =0; j < alltd.length; j++){
        td = alltd[j]
            if (td) {
                if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
                    present = true
                    tr[i].style.display = "";
                }
            }
    }

    if(present == false && i !== 0){
                tr[i].style.display = "none";
    }

  }
}
