'use strict';
(function ($) {

// --------------------------------------------------------------------------
var fixedMenuShowAtLeastOne = false;
var fixedMenuLastTimeInMillis = (new Date()).getTime();
var TIMEOUT_DURATION = 15 * 1000;

function setFixedMenuVisible(visible, isUserAction) {
    var panel = $('#style-switcher');
    var width = $("#style-switcher-panel").width();
    if (visible && !panel.hasClass('active')) { // Want to Show
        panel.addClass('active');
        panel.animate({
            right: 0
        }, width);
        $('#style-switcher-toggle').removeClass("off");
        $('#style-switcher-toggle').addClass("on");
        fixedMenuShowAtLeastOne = true;
        fixedMenuLastTimeInMillis = (new Date()).getTime();
    } else if (!visible && panel.hasClass('active')) { // Want to Hide
        panel.animate({
            right: -width
        }, width);
        panel.removeClass('active');
        $('#style-switcher-toggle').removeClass("on");
        $('#style-switcher-toggle').addClass("off");
        fixedMenuLastTimeInMillis = (new Date()).getTime();
    }
}
// --------------------------------------------------------------------------
function setOnClickFixedMenu() {
    $("#style-switcher a[name='top']").remove();
    $('#style-switcher-toggle').on('click', function(e) {
        var panel = $('#style-switcher');
        var visible = !panel.hasClass('active');
        setFixedMenuVisible(visible, true);
    });
}
    /*------------------ Preloader   --------------------*/
    $(window).on('load', function () {
        $(".loader").fadeOut();
        $("#preloder").delay(200).fadeOut("slow");
        /*------------------      Product filter --------------------*/
        $('.filter__controls li').on('click', function () {
            $('.filter__controls li').removeClass('active');
            $(this).addClass('active');
        });
        if ($('.property__gallery').length > 0) {
            var containerEl = document.querySelector('.property__gallery');
            var mixer = mixitup(containerEl);
        }
    });
    /*------------------ Background Set  --------------------*/
    $('.set-bg').each(function () {
        var bg = $(this).data('setbg');
        $(this).css('background-image', 'url(' + bg + ')');
    });
    //Search Switch
    $('.search-switch').on('click', function () {
        $('.search-model').fadeIn(400);
    });
    $('.search-close-switch').on('click', function () {
        $('.search-model').fadeOut(400, function () {
            $('#search-input').val('');
        });
    });
    //Canvas Menu
    $(".canvas__open").on('click', function () {
        $(".offcanvas-menu-wrapper").addClass("active");
        $(".offcanvas-menu-overlay").addClass("active");
    });
    $(".offcanvas-menu-overlay, .offcanvas__close").on('click', function () {
        $(".offcanvas-menu-wrapper").removeClass("active");
        $(".offcanvas-menu-overlay").removeClass("active");
    });
    /*------------------	Navigation	--------------------*/
    $(".header__menu").slicknav({
        prependTo: '#mobile-menu-wrap',
        allowParentLinks: true
    });
    /*------------------      Accordin Active    --------------------*/
    $('.collapse').on('shown.bs.collapse', function () {
        $(this).prev().addClass('active');
    });
    $('.collapse').on('hidden.bs.collapse', function () {
        $(this).prev().removeClass('active');
    });
    /*--------------------------   Banner Slider  ----------------------------*/
    $(".banner__slider").owlCarousel({
        loop: true,
        margin: 0,
        items: 1,
        dots: true,
        smartSpeed: 1200,
        autoHeight: false,
        autoplay: true
    });
    /*--------------------------  Product Details Slider  ----------------------------*/
    $(".product__details__pic__slider").owlCarousel({
        loop: false,
        margin: 0,
        items: 1,
        dots: false,
        nav: true,
        navText: ["<i class='arrow_carrot-left'></i>","<i class='arrow_carrot-right'></i>"],
        smartSpeed: 1200,
        autoHeight: false,
        autoplay: false,
        mouseDrag: false,
        startPosition: 'URLHash'
    }).on('changed.owl.carousel', function(event) {
        var indexNum = event.item.index + 1;
        product_thumbs(indexNum);
    });
    function product_thumbs (num) {
        var thumbs = document.querySelectorAll('.product__thumb a');
        thumbs.forEach(function (e) {
            e.classList.remove("active");
            if(e.hash.split("-")[1] == num) {
                e.classList.add("active");
            }
        })
    }
    /*------------------	Magnific   --------------------*/
    $('.image-popup').magnificPopup({
        type: 'image'
    });
    $(".nice-scroll").niceScroll({
        cursorborder:"",
        cursorcolor:"#dddddd",
        boxzoom:false,
        cursorwidth: 5,
        background: 'rgba(0, 0, 0, 0.2)',
        cursorborderradius:50,
        horizrailenabled: false
    });
    /*-------------------	Range Slider --------------------- */
	var rangeSlider = $(".price-range"),
    minamount = $("#minamount"),
    maxamount = $("#maxamount"),
    minPrice = rangeSlider.data('min'),
    maxPrice = rangeSlider.data('max');
    rangeSlider.slider({
    range: true,
    min: minPrice,
    max: maxPrice,
    values: [minPrice, maxPrice],
    slide: function (event, ui) {
        minamount.val('$' + ui.values[0]);
        maxamount.val('$' + ui.values[1]);
        }
    });
    minamount.val('$' + rangeSlider.slider("values", 0));
    maxamount.val('$' + rangeSlider.slider("values", 1));
    /*------------------	Single Product	--------------------*/
	$('.product__thumb .pt').on('click', function(){
		var imgurl = $(this).data('imgbigurl');
		var bigImg = $('.product__big__img').attr('src');
		if(imgurl != bigImg) {
			$('.product__big__img').attr({src: imgurl});
		}
    });
    /*-------------------	Quantity change	--------------------- */
	var flagOp = true; /* fixed double call in system??? */
	var editMode = false;
	$("div.product__details__widget").on("change", function(e){
	    if (flagOp==false) return flagOp=true;
	    else flagOp=false
        var values = [];
        $('div.product__details__widget input[type="radio"]:checked').each(function (index) {
            var that = $(this)
            values[index] = that.data("key")
        });
        console.log(values, pid, cid);
        flagOp=true
        var url = "/ajax_check_exist/";

        if(values.length < 1 || values == undefined || Number.isInteger(pid) == false || Number.isInteger(cid) == false){
            return false
        }
        $.ajax({
                    url: url,
                    data: {
                      'values': values.toString(),
                      'pid': pid,
                      'cid': cid,
                    },
                    beforeSend: function(){
                        if(values.length < 1 || values == undefined || Number.isInteger(pid) == false || Number.isInteger(cid) == false){
                            return false
                        }
                        editMode = true;
                        console.log(values);
                    },
                    success: function (options) {
                        if (typeof(options) !== 'undefined' && options.curl !== null) {
                            window.location.assign(options.curl);
                        }
                        console.log(options);
                        editMode = false;
                    },
                    error: function(data) {
                        editMode = false;
                    },
                    complete: function(data) {
                        editMode = false;
                    }
                });
    });
	$("#selPro").on('change', function (e) {
	    e.preventDefault();
	    e.stopPropagation();
      var $this = $(this);
      var href = $(this).children("option:selected").attr("data-href");
      try { window.location.assign(href); }
      catch(err) { window.location.href=href; }

    });
	var wto;
	$("#inQty").on('change keypress paste focus textInput input', function () {
      var $this = $(this);
      clearTimeout(wto);
      wto = setTimeout(function() {
          var minQty = $this.attr("data-min");
          var maxQty = $this.attr("data-max");
          var curValue = $this.val();
          if (curValue < minQty) curValue = minQty
          else
            if (curValue > maxQty) curValue = maxQty
          $this.val(curValue);
      }, 1500);
    });
    var proQty = $('.pro-qty');
	proQty.prepend('<span class="dec qtybtn">-</span>');
	proQty.append('<span class="inc qtybtn">+</span>');
	proQty.on('click', '.qtybtn', function () {
		var $button = $(this);
		var $inQty = $button.parent().find('input')
		var oldValue = $button.parent().find('input').val();
		var minQty = $inQty.attr("data-min");
		var maxQty = $inQty.attr("data-max");
		if ($button.hasClass('inc')) {
			var newVal = parseFloat(oldValue) + 1;
		} else {
			// Don't allow decrementing below zero
			if (oldValue > 1) {
				var newVal = parseFloat(oldValue) - 1;
			} else {
				var newVal = 1;
			}
		}
		if (newVal > maxQty) {
			newVal = maxQty;
		}
		$button.parent().find('input').val(newVal);
    });
    /*-------------------	Radio Btn	--------------------- */
    $(".size__btn label").on('click', function () {
        $(".size__btn label").removeClass('active');
        $(this).addClass('active');
    });
})(jQuery);