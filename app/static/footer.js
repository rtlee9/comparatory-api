function set_bottom() {

  var docHeight = $(window).height();
  var footerHeight = $('#footer').outerHeight();
  var footerTop = $('#footer').position().top + footerHeight;

  if (footerTop < docHeight) {
    $('#footer').css('margin-top', 0 + (docHeight - footerTop) + 'px');
  }
}

$(document).ready(set_bottom());

$( window ).resize(set_bottom);
