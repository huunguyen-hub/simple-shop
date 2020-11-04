function isInt(value) {
  return !isNaN(value) && (function(x) { return (x | 0) === x; })(parseFloat(value))
}
var contain = null;
var initialLoad = true;
window.addEventListener("load", function(event) {
    (function($) {
        var prefix = 'id_featureproduct_set-';
        var suffix = '-feature_id';
        $("select[name^='"+prefix+"']" && "select[name$='"+suffix+"']").change(function() {
            console.log(initialLoad);
            if (initialLoad) return initialLoad;
            var id = $(this).attr("id");
            split_string = id.split(/(\d+)/)
            if (split_string.length === 3 && !isNaN(split_string[1]) && (split_string[0]==prefix) && (split_string[2]==suffix)){
                var field ='feature_value_id';
                var relation = split_string[0] + split_string[1] + "-" + field
                var url = "/ajax_chained_view/";  // get the url of the `load_cities` view
                var value = $(this).val();  // get the selected country ID from the HTML input
                var contain = this;
                if(isInt(value)){
                $.ajax({
                    url: url,
                    data: {
                      'parent_value': value,
                      'parent_field': 'feature_id',
                      'field': field,
                      'field_value': 'value',
                      'field_obj': 'FeatureValue',
                    },
                    beforeSend: function(){
                        $("#"+relation).empty();
                    },
                    success: function (options) {   // `data` is the return of the `load_cities` view function
                        var optionsHTML = "";
                        options.forEach(function(option) {
                            optionsHTML += '<option value="' + option[0] + '">' + option[1] + '</option>';
                        });
                        var valueField = document.getElementById(relation);
                        if ((valueField !== null)&&(valueField !== undefined)) {
                            valueField.innerHTML = optionsHTML;
                            valueField.dispatchEvent(new Event("change"));
                            valueField.dispatchEvent(new Event("load"));
                            valueField.dispatchEvent(new Event("liszt:updated")); // support for chosen versions < 1.0.0
                            valueField.dispatchEvent(new Event("chosen:updated")); // support for chosen versions >= 1.0.0
                        }
                    }
                });
            }
            }
        });

        $("#id_feature_id").change(function () {
              var url = "/ajax_chained_view/";  // get the url of the `load_cities` view
              var value = $(this).val();  // get the selected country ID from the HTML input
              contain = this;
            if(isInt(value)){
                $.ajax({
                    url: url,
                    data: {
                      'parent_value': value,
                      'parent_field': 'feature_id',
                      'field': 'feature_value_id',
                      'field_value': 'value',
                      'field_obj': 'FeatureValue',
                    },
                    beforeSend: function(){
                        $('#id_feature_value_id').empty();
                    },
                    success: function (options) {   // `data` is the return of the `load_cities` view function
                        var optionsHTML = "";
                        options.forEach(function(option) {
                            optionsHTML += '<option value="' + option[0] + '">' + option[1] + '</option>';
                        });
                        var valueField = document.getElementById('id_feature_value_id');
                        if ((valueField !== null)&&(valueField !== undefined)) {
                            valueField.innerHTML = optionsHTML;
                            valueField.dispatchEvent(new Event("change"));
                            valueField.dispatchEvent(new Event("load"));
                            valueField.dispatchEvent(new Event("liszt:updated")); // support for chosen versions < 1.0.0
                            valueField.dispatchEvent(new Event("chosen:updated")); // support for chosen versions >= 1.0.0
                        }
                    }
                });
            }
        });


        $("#id_attr_group_id").change(function () {
              var url = "/ajax_chained_view/";  // get the url of the `load_cities` view
              var value = $(this).val();  // get the selected country ID from the HTML input
              contain = this;
            if(isInt(value)){
                $.ajax({
                    url: url,
                    data: {
                      'parent_value': value,
                      'parent_field': 'attr_group_id',
                      'field': 'attribute_id',
                      'field_value': 'name',
                      'field_obj': 'Attribute',
                    },
                    beforeSend: function(){
                        $('#id_attribute_id').empty();
                    },
                    success: function (options) {   // `data` is the return of the `load_cities` view function
                        var optionsHTML = "";
                        options.forEach(function(option) {
                            optionsHTML += '<option value="' + option[0] + '">' + option[1] + '</option>';
                        });
                        var valueField = document.getElementById('id_attribute_id');
                        if ((valueField !== null)&&(valueField !== undefined)) {
                            valueField.innerHTML = optionsHTML;
                            valueField.dispatchEvent(new Event("change"));
                            valueField.dispatchEvent(new Event("load"));
                            valueField.dispatchEvent(new Event("liszt:updated")); // support for chosen versions < 1.0.0
                            valueField.dispatchEvent(new Event("chosen:updated")); // support for chosen versions >= 1.0.0
                        }
                    }
                });
            }
        });

        $(document).mousedown(function(event){
            switch(event.which)
            {
                case 1:
                case 2:
                case 3:
                    initialLoad = false;
                break;
            }
            if ((event.originalEvent.isTrusted === true && event.originalEvent.isPrimary === undefined) || event.originalEvent.isPrimary === true) {
                initialLoad = false;
            }
            return true;// to allow the browser to know that we handled it.
        });
    })(django.jQuery);
});


