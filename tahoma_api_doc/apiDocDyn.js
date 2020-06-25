$(document).ready(function() {
    window.showAll = true;
    window.showDeprecated = false;
    $(".fh").hide();

    $(".fs").on('click', function() {
        $(this).parent().children('tr').each(function(n,v){if (n>0) $(v).toggle();});

/*
        if (!ts.is(":visible")) {
            ts.slideToggle('slow');
        } else {
            ts.slideUp("fast");
        }
*/
    });

    $(".classRef").on('click', function() {
        toggle($(this));
/*
                if (!n.eq(index).is(":visible")) {
                    n.eq(index).slideToggle('slow');
                } else {
                    n.eq(index).slideUp("fast");
                }
*/
    });

    $(".list").on('click', function() {
        var t = $(this).parent().parent().parent().children('tr');
        $.each(t, function(index, val) {
            if (index >= 1) {
                $(this).children('td').children('table').children('tbody').children('tr').eq(2).slideUp("fast");
            }
        });
    });

    $(".expand").on('click', function() {
        var t = $(this).parent().parent().parent().children('tr');
        $.each(t, function(index, val) {
            if (index >= 1) {
                $(this).children('td').children('table').children('tbody').children('tr').each(function(n,v){if (n>0) $(v).toggle();});
            }
        });
    });

    $(".moreDefClass").on('click', function() {
    	var etc = $(this).parent().children("span").eq(0);
    	var more = $(this).parent().children("span").eq(1);
    	if(!more.is(":visible")) {
    		more.show();
    		etc.hide();
    		$(this).text("Read less");
    	}
    	else {
    		more.hide();
    		etc.show();
    		$(this).text("Read more");
    	}
    });

    $(".moreAVS").on('click', function() {
    	var moreAVS=$(this);
    	var avsTable = $(this).parent().children("table");
    		if(moreAVS.text()=="See Allowed Values") {
				$.each(avsTable, function(index, val) {
					$(this).show();
				});
        		moreAVS.text("Hide Allowed Values");
        	}
        	else {
        		$.each(avsTable, function(index, val) {
        			$(this).hide();
				});
        		$(this).text("See Allowed Values");
        	}

    });

    $(".moreATS").on('click', function() {
    	var moreATS=$(this);
    	var atsTable = $(this).parent().children("table");
    		if(moreATS.text()=="See Allowed Types") {
				$.each(atsTable, function(index, val) {
					$(this).show();
				});
        		moreATS.text("Hide Allowed Types");
        	}
        	else {
        		$.each(atsTable, function(index, val) {
        			$(this).hide();
				});
        		$(this).text("See Allowed Types");
        	}

    });

    $("#listAll").on('click', function () {
        window.showAll = !window.showAll;
        var deprecatedSelector = !window.showDeprecated ? ":not(:has(.deprecated)), :has(.section)" : "";
        var elems = $('.classRef').parent().parent().siblings(deprecatedSelector);
        if (window.showAll) {
            elems.show();
            $('.classRef').removeClass('closed');
        }
        else {
            elems.hide();
            $('.classRef').addClass('closed');
        }
    });

    $("#showHideDeprecated").on('click', function () {
        window.showDeprecated = !window.showDeprecated;
        $('.classRef').parent().parent().siblings(":not(:has(.closed, .section)) :has(.deprecated)").toggle();
    });

    function toggle(elem) {
        elem.toggleClass('closed')
        var hasSubClasses = elem.parent().parent().parent().find('.section').length > 0
        var deprecatedSelector = !(hasSubClasses || window.showDeprecated) ? ":not(:has(.deprecated))" : "";
        elem.parent().parent().siblings(deprecatedSelector).toggle();
    }

});
