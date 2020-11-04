/* global CKEDITOR */
window.addEventListener("load", function() {
    (function($) {
        var el = document.getElementById('ckeditor-init-script');
        if (el && !window.CKEDITOR_BASEPATH) {
            window.CKEDITOR_BASEPATH = el.getAttribute('data-ckeditor-basepath');
        }
        if( typeof(CKEDITOR) !== "undefined" ){
        CKEDITOR.on('instanceReady', function (ev) {
            ev.editor.dataProcessor.htmlFilter.addRules( {
                elements : {
                    img: function( el ) {
                        el.addClass('img-responsive');
                        var style = el.attributes.style;
                        if (style) {
                            var match = /(?:^|\s)width\s*:\s*(\d+)px/i.exec(style),
                                width = match && match[1];
                            match = /(?:^|\s)height\s*:\s*(\d+)px/i.exec(style);
                            var height = match && match[1];
                            if (width) {
                                el.attributes.style = el.attributes.style.replace(/(?:^|\s)width\s*:\s*(\d+)px;?/i, '');
                                el.attributes.width = width;
                            }
                            if (height) {
                                el.attributes.style = el.attributes.style.replace(/(?:^|\s)height\s*:\s*(\d+)px;?/i, '');
                                el.attributes.height = height;
                            }
                        }
                        if (!el.attributes.style)
                            delete el.attributes.style;
                    }
                }
            });
        });
        CKEDITOR.on('dialogDefinition', function(ev){
        var dialogName = ev.data.name;
        var dialogDefinition = ev.data.definition;
        dialogDefinition.onLoad = function () {
                var dialog = CKEDITOR.dialog.getCurrent();
                this.selectPage('Upload');
                var uploadTab = dialogDefinition.getContents('Upload');
                for (var i = 0; i < uploadTab.elements.length; i++) {
                    var el = uploadTab.elements[i];
                    console.log(el.type);
                    if (el.type !== 'fileButton') {
                        continue;
                    }
                }

                var uploadButton = uploadTab.get('uploadButton');
                uploadButton['filebrowser']['onSelect'] = function( fileUrl, errorMessage ) {
                    //$("input.cke_dialog_ui_input_text").val(fileUrl);
                    dialog.getContentElement('info', 'txtUrl').setValue(fileUrl);
                    //$(".cke_dialog_ui_button_ok span").click();
                }
                // on tab switching or automatic after upload
                this.on('selectPage', function (e) {
                    // show okay button of ckeditor dialog
                    document.getElementById(this.getButton('ok').domId).style.display='inline';
                    // after upload the selectPage is fired, show Page-Info then
                    dialog.showPage( 'info' );
                });
            }
         if (dialogName === 'image' || dialogName === 'image2') {
            var uploadTab = dialogDefinition.getContents('Upload');
            // Remove the 'Link' and 'Advanced' tabs from the 'Image' dialog.
            dialogDefinition.removeContents( 'Link' );
            dialogDefinition.removeContents( 'advanced' );
            // Get a reference to the 'Image Info' tab.
            var infoTab = dialogDefinition.getContents( 'info' );
            // Remove unnecessary widgets/elements from the 'Image Info' tab.
            infoTab.remove( 'txtHSpace');
            infoTab.remove( 'txtVSpace');
         }
    });
    }
    })(django.jQuery);
});