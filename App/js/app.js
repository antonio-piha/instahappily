
(function( $ ) {
$(() => {
  (() => {
  })();

  // didn't like it - Animations initialization
  //new WOW().init();

  let emoji = new wEmoji();

  // Initialise lists
  $('.js-list').each(function (i, element) {
    $(element).list({
      on_add_item: ($item) => {
        emoji.discover($item);
      }
    });
  });

  $('.js-list-static').each(function (i, element) {
    $(element).list({
      static_list: true,
      filter_by_input: false
    });
  });

  // Double check popups for submitting forms
  $('.js-submit-confirmation-popover').each((i, element) => {
    $(element).submit_confirmation();
  });

  // Form validation - just required fields
  $('form').submit(function(){
    let $form = $(this);
    let valid = true;
    $form.find('[required]').each(function() {
        let $errors = $(this).siblings('.js-errors');
        if ($(this).val() === '') {
          valid = false;
          $errors.text('Required');
        } else {
          $errors.text('');
        }
    });
    return valid;
  });

  // This is for form submits that are outside of the forms they need to submit
  $('[data-form-to-submit]').click(function () {
    let form_id = $(this).data('formToSubmit');
    let additional_query_params = $(this).data('additionalQueryParams');
    let $form = $('.' + form_id);
    if (!$form.length) {
       return;
    }

    if (additional_query_params) {
      additional_query_params = additional_query_params.replace(/'/g, '"');
      additional_query_params = JSON.parse(additional_query_params);
      // let action = $form.attr('action');
      // if (action.indexOf('?') == -1) {
      //     action += '?';
      // }
      // // Add & if it has more params
      // if (action.substr(-1) != '?') {
      //   action += '&';
      // }
      // action = action + $.param(additional_query_params);
      Object.keys(additional_query_params).forEach(function(key) {
        let value = additional_query_params[key];
        var $input = $('<input type="hidden" />')
        $input.attr('name', key);
        $input.val(value);
        $form.append($input);
      });
      // $form.attr('action', action);
    }
    $form.submit();
  });

  // Session settings listener
  $('.js-session-settings-action-listener')
    .on('click', '.js-settings-action-input-help', function() {
      // To enable input helpers
      let value = $(this).data('value');

      $(this).parents('.js-settings-element-input-parent').find('input')
        .focus()
        .val(value);
      return false;
    });

  // Settings info collapsibles
  let settings_collapse_last_state = 'hide';
  $collapsibles_to_skip = $('nav .collapse');
  $collapsibles = $('.collapse').not($collapsibles_to_skip);
  $('.js-action-toggle-all-settings-help').on('click', function() {
    if (settings_collapse_last_state === 'hide') {
      $collapsibles.collapse('show');
      settings_collapse_last_state ='show';
    } else {
      $collapsibles.collapse('hide');
      settings_collapse_last_state ='hide';
    }
  });

  // Toggle displayed settings for different modes: simple, advanced, expert
  visibility_toggled_elements = $('.js-visibility-toggle');
  visibility_toggled_elements_advanced = visibility_toggled_elements.filter('.js-advanced');
  visibility_toggled_elements_expert = visibility_toggled_elements.filter('.js-expert');
  $('.js-action-change-settings-view-level').on('click', 'a', function(e) {
    anchor = $(this);
    level = anchor.data('level');
    // set up active class on correct element
    anchor.siblings().removeClass('active')
    anchor.addClass('active');

    if (level === 'expert') {
      visibility_toggled_elements.removeClass('d-none');
    } else if (level === 'advanced') {
      visibility_toggled_elements_expert.addClass('d-none');
      visibility_toggled_elements_advanced.removeClass('d-none');
    } else {
      visibility_toggled_elements.addClass('d-none');
    }

    // disable link
    e.preventDefault();
  });

  // Profile filter in navigation bar
  $('.js-nav-profile-list')
  .on('input', 'input', function() {
    let parent = $(this).parents('.js-nav-profile-list');
    let filter = $(this).val();
    filter_lowercase = filter.toLowerCase();

    profile_items = parent.find('.js-nav-profile-list-item');
    profile_items.show();

    let filter_function = function () {
      return $( this ).text().toLowerCase().indexOf( filter_lowercase ) >= 0;
    }
    profile_items.each(function(i, profile_item){
      profile_item = $(profile_item);
      profile_item_name = profile_item.find('.nav-text:first');
      if (!profile_item_name.filter(filter_function).length > 0) {
        profile_item.hide();
      }
    });

    return false;
  });

  // Password field is hidden on profile settings page
  $('.js-reveal-password-field').on('click', function() {
    $(this).addClass('d-none');
    $('.js-hidden-password-field').removeClass('d-none');
  });



  // Animation when loading and unloading the site
  let page_loader = $('.js-page-loader');
  page_loader.addClass('d-none');
  $(window).on("beforeunload", function(event) {
    page_loader.removeClass('d-none');
  });

  // Follower Following tool
  $follow_following_tool = $('.js-follower-following-tool-create-request');
  $follow_following_tool_unfollowers_fields = $('.js-follower_following_tool_unfollowers_fields');
  if ($follow_following_tool.length > 0) {
    $follow_following_tool.find('.js-follower_following_tool_type')
      .find('select').on('change', function() {
        value = this.value;
        $follow_following_tool_unfollowers_fields
          .addClass('d-none');
        if (value.indexOf('unfollow') > -1) {
          $follow_following_tool_unfollowers_fields
            .removeClass('d-none');
        }
      });
  }

  // DataTables
  wDataTables.init();

  // CustomLists
  wCustomLists.init();

  // Let's call this last
  // Has to be called after initialising list because of the list templates
  emoji.discover();

  // Important
  console.log(/*atob(*/'VGlzIHRydWUgd2l0aG91dCBseWluZywgY2VydGFpbiBhbmQgbW9zdCB0cnVlLiBUaGF0IHdoaWNoIGlzIGJlbG93IGlzIGxpa2UgdGhhdCB3aGljaCBpcyBhYm92ZSBhbmQgdGhhdCB3aGljaCBpcyBhYm92ZSBpcyBsaWtlIHRoYXQgd2hpY2ggaXMgYmVsb3cgdG8gZG8gdGhlIG1pcmFjbGVzIG9mIG9uZSBvbmx5IHRoaW5nLiAgLSBUaGUgRW1lcmFsZCBUYWJsZXQ='/*)*/)
});
}(jQuery));