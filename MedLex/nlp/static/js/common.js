$(function() {
    $( window ).resize(function() {
        onResize();
    });
    onResize();
});

function onResize() {
    var mHeaderNavHeight = $("#m_header_nav").height();
    var bodyPaddingTop = parseInt($(".m-header--fixed .m-body").css('padding-top'));

    if(mHeaderNavHeight > 70 ) {
        var paddingTop = mHeaderNavHeight - bodyPaddingTop + 20;
        if(bodyPaddingTop == 60)
            paddingTop += 50;
        $(".m-content").css('padding-top', paddingTop + 'px');
        // alert(paddingTop);
    } else {
        $(".m-content").css('padding-top', '');
    }
}