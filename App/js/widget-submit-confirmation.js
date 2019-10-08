(function( $ ) {
  /**
   * Submit confirmation $self plugin jQuery
   */
  $.fn.submit_confirmation = function(options) {

    let $self = $(this);
    if ($self.length != 1) {
      throw "Must be called on one element."
    }

    let defaults = {
      title: 'Double check',
      placement: 'bottom'
    };

    let settings = $.extend( true, {}, defaults, options );

    let initiated = false;
    let $content = null;
    let $form = null;
    let $fake_submit = null;

    //##################################################
    let init = () => {
      $form = $self.parent('form');
      $fake_submit = $form.find('.js-fake-submit');
      $content = $self.children().eq(0);

      // After this point we can't continue if it was initated
      if (initiated) { return ;}

      create_popover();
      bind_events();
      initiated = true;
    }

    let bind_events = () => {
      $content
      .on('click', 'button', () => {
        $form.submit();
      });
    }

    let create_popover = () => {
      if ($fake_submit.length == 0)
        return;

      $fake_submit.popover({
        title: settings.title,
        trigger: 'focus',
        html: true,
        content: $content,
        placement: settings.placement
      });
    }

    //##################################################

    init();

    return this;
   };

 }( jQuery ));
