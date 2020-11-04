var Layout = function () {
     // IE mode
    var isRTL = false;
    var isIE8 = false;
    var isIE9 = false;
    var isIE10 = false;
    var isIE11 = false;

    var responsive = true;
    var responsiveHandlers = [];
    var handleInit = function() {
        if ($('body').css('direction') === 'rtl') {
            isRTL = true;
        }
        isIE8 = !! navigator.userAgent.match(/MSIE 8.0/);
        isIE9 = !! navigator.userAgent.match(/MSIE 9.0/);
        isIE10 = !! navigator.userAgent.match(/MSIE 10.0/);
        isIE11 = !! navigator.userAgent.match(/MSIE 11.0/);
        
        if (isIE10) {
            jQuery('html').addClass('ie10'); // detect IE10 version
        }
        if (isIE11) {
            jQuery('html').addClass('ie11'); // detect IE11 version
        }
    }

    // runs callback functions set by App.addResponsiveHandler().
    var runResponsiveHandlers = function () {
        // reinitialize other subscribed elements
        for (var i in responsiveHandlers) {
            var each = responsiveHandlers[i];
            each.call();
        }
    }

    // handle the layout reinitialization on window resize
    var handleResponsiveOnResize = function () {
        var resize;
        if (isIE8) {
            var currheight;
            $(window).resize(function () {
                if (currheight == document.documentElement.clientHeight) {
                    return; //quite event since only body resized not window.
                }
                if (resize) {
                    clearTimeout(resize);
                }
                resize = setTimeout(function () {
                    runResponsiveHandlers();
                }, 50); // wait 50ms until window resize finishes.                
                currheight = document.documentElement.clientHeight; // store last body client height
            });
        } else {
            $(window).resize(function () {
                if (resize) {
                    clearTimeout(resize);
                }
                resize = setTimeout(function () {
                    runResponsiveHandlers();
                }, 50); // wait 50ms until window resize finishes.
            });
        }
    }

    // Handles scrollable contents using jQuery SlimScroll plugin.
    var handleScrollers = function () {
        $('.scroller').each(function () {
            var height;
            if ($(this).attr("data-height")) {
                height = $(this).attr("data-height");
            } else {
                height = $(this).css('height');
            }
            $(this).slimScroll({
                allowPageScroll: true, // allow page scroll when the element scroll is ended
                size: '7px',
                color: ($(this).attr("data-handle-color")  ? $(this).attr("data-handle-color") : '#bbb'),
                railColor: ($(this).attr("data-rail-color")  ? $(this).attr("data-rail-color") : '#eaeaea'),
                position: isRTL ? 'left' : 'right',
                height: height,
                alwaysVisible: ($(this).attr("data-always-visible") == "1" ? true : false),
                railVisible: ($(this).attr("data-rail-visible") == "1" ? true : false),
                disableFadeOut: true
            });
        });
    }

    var handleFancybox = function () {
        if (!jQuery.fancybox) {
            return;
        }
        
        jQuery(".fancybox-fast-view").fancybox();

        if (jQuery(".fancybox-button").size() > 0) {            
            jQuery(".fancybox-button").fancybox({
                groupAttr: 'data-rel',
                prevEffect: 'none',
                nextEffect: 'none',
                closeBtn: true,
                helpers: {
                    title: {
                        type: 'inside'
                    }
                }
            });

            $('.fancybox-video').fancybox({
                type: 'iframe'
            });
        }
    }

    // Handles Bootstrap Accordions.
    var handleAccordions = function () {
        jQuery('body').on('shown.bs.collapse', '.accordion.scrollable', function (e) {
            Layout.scrollTo($(e.target), -100);
        });
    }


    var handleMobiToggler = function () {
        $(".mobi-toggler").on("click", function(event) {
            event.preventDefault();//the default action of the event will not be triggered
            $(".header").toggleClass("menuOpened");
            $(".header").find(".header-navigation").toggle(300);
        });
    }

    var handleTheme = function () {
        var panel = $('.color-panel');
        // handle theme colors
        var setColor = function (color) {
            $('#style-color').attr("href", "/static/css/themes/" + color + ".css");
            $('.corporate .site-logo img').attr("src", "/static/img/logos/logo-corp-" + color + ".png");
            $('.ecommerce .site-logo img').attr("src", "/static/img/logos/logo-shop-" + color + ".png");
        }

        $('.icon-color', panel).click(function () {
            $('.color-mode').show();
            $('.icon-color-close').show();
        });

        $('.icon-color-close', panel).click(function () {
            $('.color-mode').hide();
            $('.icon-color-close').hide();
        });

        $('li', panel).click(function () {
            var color = $(this).attr("data-style");
            setColor(color);
            $('.inline li', panel).removeClass("current");
            $(this).addClass("current");
        });
    }
	
    return {
        init: function () {
            handleTheme();
            handleInit();
            handleResponsiveOnResize();
            handleFancybox();
            handleAccordions();
            handleScrollers();
            handleMobiToggler();
        },
        initSliderRange: function () {
            $( "#slider-range" ).slider({
              range: true,
              min: 0,
              max: 500,
              values: [ 50, 250 ],
              slide: function( event, ui ) {
                $( "#amount" ).val( "$" + ui.values[ 0 ] + " - $" + ui.values[ 1 ] );
              }
            });
            $( "#amount" ).val( "$" + $( "#slider-range" ).slider( "values", 0 ) +
            " - $" + $( "#slider-range" ).slider( "values", 1 ) );
        },

        // wrapper function to scroll(focus) to an element
        scrollTo: function (el, offeset) {
            var pos = (el && el.size() > 0) ? el.offset().top : 0;
            if (el) {
                if ($('body').hasClass('page-header-fixed')) {
                    pos = pos - $('.header').height(); 
                }            
                pos = pos + (offeset ? offeset : -1 * el.height());
            }

            jQuery('html,body').animate({
                scrollTop: pos
            }, 'slow');
        },
        //public function to add callback a function which will be called on window resize
        addResponsiveHandler: function (func) {
            responsiveHandlers.push(func);
        },
        scrollTop: function () {
            App.scrollTo();
        }
    };
}();