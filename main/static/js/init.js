function isInt(value) {
  return !isNaN(value) && (function(x) { return (x | 0) === x; })(parseFloat(value))
}
var initialLoad = true;
window.addEventListener("load", function(event) {
    (function($) {
        $("#id_city_id").change(function () {
              var url = "/ajax_chained_view/";  // get the url of the `load_cities` view
              var value = $(this).val();  // get the selected country ID from the HTML input
              var contain = $(this);
            if(isInt(value) && initialLoad){
                $.ajax({
                    url: url,
                    data: {
                      'parent_value': value,
                      'parent_field': 'city_id',
                      'field': 'district_id',
                      'field_value': 'name',
                      'field_obj': 'District',
                    },
                    beforeSend: function(){
                        initialLoad = false;
                        $('#id_district_id').empty();
                        $('#id_ward_id').empty();
                    },
                    success: function (options) {   // `data` is the return of the `load_cities` view function
                        var optionsHTML = "";
                        options.forEach(function(option) {
                            optionsHTML += '<option value="' + option[0] + '">' + option[1] + '</option>';
                        });

                        var valueField = contain.parent().closest('div.row').find('#id_district_id');
                        if ((valueField !== null)&&(valueField !== undefined)) {
                            valueField.html(optionsHTML).trigger('change');
                        }
                        initialLoad = true;
                    },
                    error: function(data) {
                        initialLoad = true;
                    },
                    complete: function(data) {
                        initialLoad = true;
                    }
                });
            }
        });
        $("#id_district_id").change(function () {
              var url = "/ajax_chained_view/";  // get the url of the `load_cities` view
              var value = $(this).val();  // get the selected country ID from the HTML input
              var contain = $(this);
            if(isInt(value) && initialLoad){
                $.ajax({
                    url: url,
                    data: {
                      'parent_value': value,
                      'parent_field': 'district_id',
                      'field': 'ward_id',
                      'field_value': 'name',
                      'field_obj': 'Ward',
                    },
                    beforeSend: function(){
                        initialLoad = false;
                        $('#id_ward_id').empty();
                    },
                    success: function (options) {   // `data` is the return of the `load_cities` view function
                        var optionsHTML = "";
                        options.forEach(function(option) {
                            optionsHTML += '<option value="' + option[0] + '">' + option[1] + '</option>';
                        });

                        var valueField = contain.parent().closest('div.row').find('#id_ward_id');
                        if ((valueField !== null)&&(valueField !== undefined)) {
                            valueField.html(optionsHTML).trigger('change');
                        }
                        initialLoad = true;
                    },
                    error: function(data) {
                        initialLoad = true;
                    },
                    complete: function(data) {
                        initialLoad = true;
                    }
                });
            }
        });
    })(jQuery);
});


