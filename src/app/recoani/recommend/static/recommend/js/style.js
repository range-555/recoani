
$(function () {

  // WORKSモーダル開閉
  var modalWinTop
  $('.result__card__modal-link').each(function () {
    $(this).on('click', function () {
      modalWinTop = $(window).scrollTop();
      var target = $(this).data('target');
      var modal = document.getElementById(target);
      $(modal).fadeIn();
      return false;
    });
  });
  $('.modal__close').on('click', function () {
    $('.modal').fadeOut();
    $('body,html').stop().animate({
      scrollTop: modalWinTop
    }, 100);
    return false;
  });

});