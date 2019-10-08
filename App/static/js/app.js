(function(window, $) {
  $(() => {
    // Charts
    if (window.activity_records === undefined) {
      return
    }

    window.activity_records = window.activity_records || {
      'likes': [],
      'comments': [],
      'follows': [],
      'unfollows': [],
      'num_followers': [],
      'num_following': []
    }

    $no_data_alert = $('.js-profile-view-charts-no-data-info');
    // Check if we want to show the no data alert

    if (
      window.activity_records.likes.length == 0 ||
      window.activity_records.comments.length == 0 ||
      window.activity_records.follows.length == 0 ||
      window.activity_records.unfollows.length == 0 ||
      window.activity_records.num_followers.length == 0 ||
      window.activity_records.likes.num_following == 0
      ) {
        $no_data_alert.removeClass('d-none');
      }

    $('.js-chart-profile-likes').chart({
      label: 'Number of likes',
      data: window.activity_records.likes
    });
    $('.js-chart-profile-comments').chart({
      label: 'Number of comments',
      data: window.activity_records.comments
    });
    $('.js-chart-profile-follows').chart({
      label: 'Number of follows',
      data: window.activity_records.follows
    });
    $('.js-chart-profile-unfollows').chart({
      label: 'Number of unfollows',
      data: window.activity_records.unfollows
    });
    $('.js-chart-profile-followers').chart({
      label: 'Number of followers',
      data: window.activity_records.num_followers
    });
    $('.js-chart-profile-following').chart({
      label: 'Number of following',
      data: window.activity_records.num_following
    });
  });
}(window, jQuery));
(function( $ ) {

  $.fn.custom_list_picker = function(options) {

    let $self = $(this);
    if ($self.length != 1) {
      throw "Must be called on one element."
    }

    let defaults = {};
    let settings = $.extend( true, {}, defaults, options );

    let initiated = false;

    let list_type_key = null;
    let $modal = null;
    let $open_button = null;
    let $remove_button = null;
    let $field = null;
    let $field_input = null;
    let field_initial_value = null;
    let $field_info = null;
    let $field_info_name = null;

    //##################################################

    let init = () => {
      list_type_key = $self.data('listTypeKey');
      $modal = $('.js-custom-list-picker-modal[data-list-type-key="' + list_type_key + '"]');
      $open_button = $self.find('.js-custom-list-open-picker');
      $remove_button = $self.find('.js-custom-list-remove');
      // Field - hidden input
      $field = $self.find('.js-custom-list-field').find('.js-object-field');
      $field_input = $field.find('input');
      field_initial_value = $field.find('.js-initial-value').text();
      // Field info - display the field values
      $field_info = $self.find('.js-custom-list-field-info');
      $field_info_name =  $field_info.find('.js-custom-list-field-info-name');


      // After this point we can't continue if it was initiated
      if (initiated) { return ;}

      initiated = true;

      $modal.modal({
        show: false
      });

      $open_button.on('click', open_picker);
      $remove_button.on('click', remove)

      set_field_data_on_init();
    }

    let open_picker = () => {
      $modal.modal('show');
      // These handlers must be added here becuase we are using same modals for several openers

      // Event listeners for datables from inside modals
      $modal.on('select.datatable', (e, data) => {
        set_field_data(data);
      });
      $modal.on('deselect.datatable', unset_field_data);

      $modal.on('hide.bs.modal', () => {
        // Important, remove event handler
        $modal.off('select.datatable');
        $modal.off('deselect.datatable');
      });
    }

    let remove = () => {
      unset_field_data();
      $remove_button.addClass('d-none');
    }

    let set_field_data = (data) => {
      // Store only values
      let value = {
        id: data.id,
        name: data.name,
        list_type: data.list_type,
        source: data.source
      }
      value = JSON.stringify(value);

      $field_input.val(value);
      $field_info.removeClass('d-none');
      $field_info_name.html(
        'Using ' + '<div class="d-inline-block">' + data.source + '</div>: ' + data.name
      );

      $remove_button.removeClass('d-none');
    }

    let unset_field_data = (e) => {
      $field_input.val('');
      $field_info.addClass('d-none');
      $field_info_name.html('');
    }

    let set_field_data_on_init = () => {
      if (field_initial_value === '') return;
      let data = null;
      try {
        data = JSON.parse(field_initial_value);
      } catch(error) {
        console.log(error);
        data = null;
      }
      if (data) {
        set_field_data(data);
      }
    }
    //##################################################

    init();

    return this;
  };

}( jQuery ));



(function(window, $) {
  let init = () => {
    custom_lists_forms();
    custom_lists_pickers();
  }

  let custom_lists_forms = () => {
    $custom_list_wrapper = $('.js-custom-list-form-wrap');
    if ($custom_list_wrapper.length == 0) { return }

    let $custom_list_fields = {'usernames': null, 'hashtags': null, 'comments': null, 'locations': null, 'links': null};
    Object.keys($custom_list_fields).forEach((key) => {
      $custom_list_fields[key] = $custom_list_wrapper.find('.js-custom-list-' + key);
    });
    $custom_list_holder = $custom_list_wrapper.find('.js-custom-list-holder');
    $custom_list_storage = $custom_list_wrapper.find('.js-custom-list-storage');
    // $custom_list_type_key listener
    $custom_list_type = $custom_list_wrapper.find('.js-custom-list-type-key').find('select');
    let custom_list_type_change = function () {
      type_key = $custom_list_type.val();
      if (!type_key) return;
      // Swap
      current_list = $custom_list_holder.children().appendTo($custom_list_storage);
      $custom_list_fields[type_key].appendTo($custom_list_holder);
    }
    custom_list_type_change();
    $custom_list_type.on('change', custom_list_type_change);
  }

  let custom_lists_pickers = () => {
    $('.js-custom-list-picker').each(function (i, element) {
      $(element).custom_list_picker();
    });
  }

  window.wCustomLists = {
    init : init
  }
}(window, jQuery));
(function(window, $) {

  let dynamic_datatable_options_defaults = {
    // properties
    columns: [
      {"data":"id"},
      {"data":"name"},
      {"data":"list_type"},
      {"data":"name_html"},
      {"data":"list_type_html"},
      {"data":"source"}
    ],
    select: true,
    // events
    on_select: (data) => {}
  }

  let settings = null;

  let initialized = 0;

  let init = (options) => {
    if (initialized) { return }
    initialized = 1;

    settings = $.extend( true, {}, dynamic_datatable_options_defaults, options );

    create_static_datatables();
    create_dynamic_datatables();

    post_init();
  }

  let post_init = () => {
    $('.dataTables_length').addClass('bs-select');
  }

  let create_static_datatables = () => {
    $('.js-data-table').dataTable();
  }

  let create_dynamic_datatables = () => {
    datatables = $('.js-data-table-select');
    datatables.dataTable(settings);

    datatables.on('select.dt', ( e, dt, type, indexes )=> {
      $datatable = $(e.target);
      let data = dt.rows(indexes).data();
      data = data && data.length > 0 ? data[0] : null;

      settings.on_select.call(null, data);
      $datatable.trigger('select.datatable', data);
    });

    datatables.on('deselect.dt', ( e, dt, type, indexes )=> {
      $datatable = $(e.target);
      $datatable.trigger('deselect.datatable');
    });
  }

  // OPTIMIZE: build tables by loading data from backend
  // let get_data_for_dynamic_tables = () => {
  //   $.getJSON('/api/get-custom-lists-sorted-by-list-type')
  //     .done(function(data) {
  //       create_dynamic_datatables(data);
  //     })
  //     .fail(function() {
  //     })
  //     .always(function() {
  //     });
  // }

  window.wDataTables = {
    init: init
  };
}(window, jQuery));
(function(window, $) {
  let Emoji = class {
    constructor() {
      // Private
      // Targets should be inputs
      this.input_to_enable_selector = '[data-emojiable-for-enable]';
      this.editor_selector = '.emoji-wysiwyg-editor';
      this.element_attributes = {
        'data-emojiable' : 'true',
        'data-emoji-input' : 'unicode'
      };
      this.emoji_picker = new EmojiPicker({
        emojiable_selector: '[data-emojiable=true]',
        assetsPath : '/static/img',
        popupButtonClasses: 'far fa-smile'
      });

      // Public
      this.on_discover = () => {};
    }

    discover(root) {
      let $root = root ? $(root) : null;
      let $input_elements = null;
      if ($root) {
        $input_elements = $root.find(this.input_to_enable_selector);
      } else {
        $input_elements = $(this.input_to_enable_selector);
      }

      $input_elements.attr(this.element_attributes);

      this.emoji_picker.discover();

      this._fix_editors($input_elements);
    }

    _fix_editors($input_elements) {
      // To trigger adding .parent-has-scroll class defined in emoji/emojiarea plugin
      $input_elements.siblings(this.editor_selector).scroll();
    }
  }

  window.wEmoji = Emoji;
}(window, jQuery));
(function( $ ) {
  /**
   * Chart plugin jQuery
   */

  let months = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December'
  ];

  let chartColors = {
    red: 'rgb(255, 99, 132)',
    orange: 'rgb(255, 159, 64)',
    yellow: 'rgb(255, 205, 86)',
    green: 'rgb(75, 192, 192)',
    blue: 'rgb(54, 162, 235)',
    purple: 'rgb(153, 102, 255)',
    grey: 'rgb(201, 203, 207)'
  }

  // embedded into common config
  let common_options = {
    responsive: true,
    legend: {
      display: false
    },
    title: {
      display: false
    },
    tooltips: {
      mode: 'index',
      intersect: false,
    },
    hover: {
      animationDuration: 100
    },
    scales: {
      xAxes: [{
        type: 'time',
        time: {
          unit: 'day'
        },
        scaleLabel: {
          display: false
        }
      }],
      yAxes: [{
        ticks:{
          beginAtZero:true
        },
        type: 'linear',
        display: true,
        scaleLabel: {
          display: false
        }
      }]
    }
  };

  let common_config = {
    type: "line",
    options: common_options,
    data: {
      datasets: [{
        label: '',
        data: null,
        fill: false,
        backgroundColor: chartColors.blue,
        lineTension: 0,
        borderColor: chartColors.blue,
        borderWidth : 1
      }]
    }
  }


  /* Plugin Chart */

  $.fn.chart = function(options) {

    let $self = $(this);
    if ($self.length != 1) {
      throw "Must be called on one element."
    }

    let defaults = {
      label : '',
      data: null
    };

    let settings = $.extend( true, {}, defaults, options );

    let initiated = false;

    let $chart = null;
    let $chart_canvas = null;
    let $chart_context = null;

    //##################################################

    let init = () => {
      $chart_canvas = $self.find('canvas').get(0);

      // After this point we can't continue if it was initated
      if (initiated) { return ;}

      create_chart();
      initiated = true;
    }

    let create_chart = () => {
      $chart_context = $chart_canvas.getContext('2d');

      let cfg = $.extend( true, {}, common_config, {
        data: {
          datasets: [{
            label: settings.label,
            data: settings.data
          }]
        }
      });

      $chart = new Chart($chart_context, cfg);
    }

    //##################################################

    init();

    return this;
  };



}( jQuery ));
(function( $ ) {
  /**
   * List plugin jQuery
   */
  $.fn.list = function(options) {

    let $self = $(this);
    if ($self.length != 1) {
      throw "Must be called on one element."
    }

    let defaults = {
      on_add_item : ($item) => {},
      static_list: false,
      filter_by_input: true
    };

    let settings = $.extend( true, {}, defaults, options );

    let initiated = false;
    let list_items_count = 0;
    let $list_items = null;
    let $filter = null;
    let $metadata = null;
    let $template = null;
    let field_name = null;
    let last_index = null;

    //##################################################

    let init = () => {
      $list_items = $self.find('.js-list-items');
      $filter = $self.find('.js-list-filter');
      $metadata = $self.find('.js-list-metadata');
      $template = $self.find('.js-template').clone().eq(0);
      $items = $self.find('.js-list-item');
      list_items_count = $items.length;
      field_name = $metadata.data('fieldName');
      last_index = Number($metadata.data('lastIndex'));

      // After this point we can't continue if it was initated
      if (initiated) { return ;}

      toggle_js_list_filter();
      bind_events();
      initiated = true;
    }

    let remove_item = (remove_button) => {
      $(remove_button).parents('.js-list-item').remove();
      list_items_count--;
      toggle_js_list_filter();
    }

    let filter_list = () => {
      let filter = $(this).find('input').val();
      filter_lowercase = filter.toLowerCase();

      // Must be fetched here because of newly added elements
      // Slip if list is static, it will already have all items
      if (!settings.static_list) {
        $items = $self.find('.js-list-item');
      }

      $items.show();

      let filter_function = function () {
        if (settings.filter_by_input) {
          found = $( this ).val().toLowerCase().indexOf( filter_lowercase ) >= 0;
        } else {
          found = $( this ).text().toLowerCase().indexOf( filter_lowercase ) >= 0;
        }
        return found;
      }
      $items.each(function(i, item){
        $item = $(item)
        if (settings.filter_by_input) {
          $element_for_filtering = $item.find('input');
        } else {
          $element_for_filtering = $item;
        }

        if (!$element_for_filtering.filter(filter_function).length > 0) {
          $item.hide();
        }
      });

    }

    let get_template = () => {
      let template = $template.clone().children();
      template.find('input, select, textarea').attr('name', field_name + '-' + last_index);
      return template;
    }
    let update_last_index = () => {
      last_index++;
      $metadata.data('lastIndex', last_index);
    }

    let js_list_add_item = () => {
      update_last_index();
      let $item = get_template();
      $list_items.append($item);

      list_items_count++;
      toggle_js_list_filter();

      settings.on_add_item.call($item, $item);

      $item.find('input, textarea').focus();
    }

    let toggle_js_list_filter = () => {
      if (list_items_count > 10) {
        $filter.addClass('d-block');
      } else {
        $filter.removeClass('d-block');
      }
    }

    let bind_events = () => {
      $self
      .on('click', '.js-list-action-add', () => {
        js_list_add_item();
      })
      .on('click', '.js-list-action-remove', (event) => {
        remove_item(event.target);
      })
      .on('input', '.js-list-filter', () => {
        filter_list();
      })
      .on('keypress', '.js-list-item', (event) =>{
        var keycode = (event.keyCode ? event.keyCode : event.which);
        if (keycode == 13 && !event.shiftKey) {
          js_list_add_item();
        }
      });
    }
    //##################################################

    init();

    return this;
  };



}( jQuery ));
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
//# sourceMappingURL=data:application/json;charset=utf8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbImNoYXJ0cy5qcyIsImN1c3RvbS1saXN0cy5qcyIsImRhdGF0YWJsZXMuanMiLCJlbW9qaS5qcyIsIndpZGdldC1jaGFydC5qcyIsIndpZGdldC1saXN0LmpzIiwid2lkZ2V0LXN1Ym1pdC1jb25maXJtYXRpb24uanMiLCJhcHAuanMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQ3ZEQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUNwS0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUMzRUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FDNUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FDaEpBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FDbkpBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQ2pFQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwiZmlsZSI6ImFwcC5qcyIsInNvdXJjZXNDb250ZW50IjpbIihmdW5jdGlvbih3aW5kb3csICQpIHtcbiAgJCgoKSA9PiB7XG4gICAgLy8gQ2hhcnRzXG4gICAgaWYgKHdpbmRvdy5hY3Rpdml0eV9yZWNvcmRzID09PSB1bmRlZmluZWQpIHtcbiAgICAgIHJldHVyblxuICAgIH1cblxuICAgIHdpbmRvdy5hY3Rpdml0eV9yZWNvcmRzID0gd2luZG93LmFjdGl2aXR5X3JlY29yZHMgfHwge1xuICAgICAgJ2xpa2VzJzogW10sXG4gICAgICAnY29tbWVudHMnOiBbXSxcbiAgICAgICdmb2xsb3dzJzogW10sXG4gICAgICAndW5mb2xsb3dzJzogW10sXG4gICAgICAnbnVtX2ZvbGxvd2Vycyc6IFtdLFxuICAgICAgJ251bV9mb2xsb3dpbmcnOiBbXVxuICAgIH1cblxuICAgICRub19kYXRhX2FsZXJ0ID0gJCgnLmpzLXByb2ZpbGUtdmlldy1jaGFydHMtbm8tZGF0YS1pbmZvJyk7XG4gICAgLy8gQ2hlY2sgaWYgd2Ugd2FudCB0byBzaG93IHRoZSBubyBkYXRhIGFsZXJ0XG5cbiAgICBpZiAoXG4gICAgICB3aW5kb3cuYWN0aXZpdHlfcmVjb3Jkcy5saWtlcy5sZW5ndGggPT0gMCB8fFxuICAgICAgd2luZG93LmFjdGl2aXR5X3JlY29yZHMuY29tbWVudHMubGVuZ3RoID09IDAgfHxcbiAgICAgIHdpbmRvdy5hY3Rpdml0eV9yZWNvcmRzLmZvbGxvd3MubGVuZ3RoID09IDAgfHxcbiAgICAgIHdpbmRvdy5hY3Rpdml0eV9yZWNvcmRzLnVuZm9sbG93cy5sZW5ndGggPT0gMCB8fFxuICAgICAgd2luZG93LmFjdGl2aXR5X3JlY29yZHMubnVtX2ZvbGxvd2Vycy5sZW5ndGggPT0gMCB8fFxuICAgICAgd2luZG93LmFjdGl2aXR5X3JlY29yZHMubGlrZXMubnVtX2ZvbGxvd2luZyA9PSAwXG4gICAgICApIHtcbiAgICAgICAgJG5vX2RhdGFfYWxlcnQucmVtb3ZlQ2xhc3MoJ2Qtbm9uZScpO1xuICAgICAgfVxuXG4gICAgJCgnLmpzLWNoYXJ0LXByb2ZpbGUtbGlrZXMnKS5jaGFydCh7XG4gICAgICBsYWJlbDogJ051bWJlciBvZiBsaWtlcycsXG4gICAgICBkYXRhOiB3aW5kb3cuYWN0aXZpdHlfcmVjb3Jkcy5saWtlc1xuICAgIH0pO1xuICAgICQoJy5qcy1jaGFydC1wcm9maWxlLWNvbW1lbnRzJykuY2hhcnQoe1xuICAgICAgbGFiZWw6ICdOdW1iZXIgb2YgY29tbWVudHMnLFxuICAgICAgZGF0YTogd2luZG93LmFjdGl2aXR5X3JlY29yZHMuY29tbWVudHNcbiAgICB9KTtcbiAgICAkKCcuanMtY2hhcnQtcHJvZmlsZS1mb2xsb3dzJykuY2hhcnQoe1xuICAgICAgbGFiZWw6ICdOdW1iZXIgb2YgZm9sbG93cycsXG4gICAgICBkYXRhOiB3aW5kb3cuYWN0aXZpdHlfcmVjb3Jkcy5mb2xsb3dzXG4gICAgfSk7XG4gICAgJCgnLmpzLWNoYXJ0LXByb2ZpbGUtdW5mb2xsb3dzJykuY2hhcnQoe1xuICAgICAgbGFiZWw6ICdOdW1iZXIgb2YgdW5mb2xsb3dzJyxcbiAgICAgIGRhdGE6IHdpbmRvdy5hY3Rpdml0eV9yZWNvcmRzLnVuZm9sbG93c1xuICAgIH0pO1xuICAgICQoJy5qcy1jaGFydC1wcm9maWxlLWZvbGxvd2VycycpLmNoYXJ0KHtcbiAgICAgIGxhYmVsOiAnTnVtYmVyIG9mIGZvbGxvd2VycycsXG4gICAgICBkYXRhOiB3aW5kb3cuYWN0aXZpdHlfcmVjb3Jkcy5udW1fZm9sbG93ZXJzXG4gICAgfSk7XG4gICAgJCgnLmpzLWNoYXJ0LXByb2ZpbGUtZm9sbG93aW5nJykuY2hhcnQoe1xuICAgICAgbGFiZWw6ICdOdW1iZXIgb2YgZm9sbG93aW5nJyxcbiAgICAgIGRhdGE6IHdpbmRvdy5hY3Rpdml0eV9yZWNvcmRzLm51bV9mb2xsb3dpbmdcbiAgICB9KTtcbiAgfSk7XG59KHdpbmRvdywgalF1ZXJ5KSk7IiwiKGZ1bmN0aW9uKCAkICkge1xuXG4gICQuZm4uY3VzdG9tX2xpc3RfcGlja2VyID0gZnVuY3Rpb24ob3B0aW9ucykge1xuXG4gICAgbGV0ICRzZWxmID0gJCh0aGlzKTtcbiAgICBpZiAoJHNlbGYubGVuZ3RoICE9IDEpIHtcbiAgICAgIHRocm93IFwiTXVzdCBiZSBjYWxsZWQgb24gb25lIGVsZW1lbnQuXCJcbiAgICB9XG5cbiAgICBsZXQgZGVmYXVsdHMgPSB7fTtcbiAgICBsZXQgc2V0dGluZ3MgPSAkLmV4dGVuZCggdHJ1ZSwge30sIGRlZmF1bHRzLCBvcHRpb25zICk7XG5cbiAgICBsZXQgaW5pdGlhdGVkID0gZmFsc2U7XG5cbiAgICBsZXQgbGlzdF90eXBlX2tleSA9IG51bGw7XG4gICAgbGV0ICRtb2RhbCA9IG51bGw7XG4gICAgbGV0ICRvcGVuX2J1dHRvbiA9IG51bGw7XG4gICAgbGV0ICRyZW1vdmVfYnV0dG9uID0gbnVsbDtcbiAgICBsZXQgJGZpZWxkID0gbnVsbDtcbiAgICBsZXQgJGZpZWxkX2lucHV0ID0gbnVsbDtcbiAgICBsZXQgZmllbGRfaW5pdGlhbF92YWx1ZSA9IG51bGw7XG4gICAgbGV0ICRmaWVsZF9pbmZvID0gbnVsbDtcbiAgICBsZXQgJGZpZWxkX2luZm9fbmFtZSA9IG51bGw7XG5cbiAgICAvLyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjXG5cbiAgICBsZXQgaW5pdCA9ICgpID0+IHtcbiAgICAgIGxpc3RfdHlwZV9rZXkgPSAkc2VsZi5kYXRhKCdsaXN0VHlwZUtleScpO1xuICAgICAgJG1vZGFsID0gJCgnLmpzLWN1c3RvbS1saXN0LXBpY2tlci1tb2RhbFtkYXRhLWxpc3QtdHlwZS1rZXk9XCInICsgbGlzdF90eXBlX2tleSArICdcIl0nKTtcbiAgICAgICRvcGVuX2J1dHRvbiA9ICRzZWxmLmZpbmQoJy5qcy1jdXN0b20tbGlzdC1vcGVuLXBpY2tlcicpO1xuICAgICAgJHJlbW92ZV9idXR0b24gPSAkc2VsZi5maW5kKCcuanMtY3VzdG9tLWxpc3QtcmVtb3ZlJyk7XG4gICAgICAvLyBGaWVsZCAtIGhpZGRlbiBpbnB1dFxuICAgICAgJGZpZWxkID0gJHNlbGYuZmluZCgnLmpzLWN1c3RvbS1saXN0LWZpZWxkJykuZmluZCgnLmpzLW9iamVjdC1maWVsZCcpO1xuICAgICAgJGZpZWxkX2lucHV0ID0gJGZpZWxkLmZpbmQoJ2lucHV0Jyk7XG4gICAgICBmaWVsZF9pbml0aWFsX3ZhbHVlID0gJGZpZWxkLmZpbmQoJy5qcy1pbml0aWFsLXZhbHVlJykudGV4dCgpO1xuICAgICAgLy8gRmllbGQgaW5mbyAtIGRpc3BsYXkgdGhlIGZpZWxkIHZhbHVlc1xuICAgICAgJGZpZWxkX2luZm8gPSAkc2VsZi5maW5kKCcuanMtY3VzdG9tLWxpc3QtZmllbGQtaW5mbycpO1xuICAgICAgJGZpZWxkX2luZm9fbmFtZSA9ICAkZmllbGRfaW5mby5maW5kKCcuanMtY3VzdG9tLWxpc3QtZmllbGQtaW5mby1uYW1lJyk7XG5cblxuICAgICAgLy8gQWZ0ZXIgdGhpcyBwb2ludCB3ZSBjYW4ndCBjb250aW51ZSBpZiBpdCB3YXMgaW5pdGlhdGVkXG4gICAgICBpZiAoaW5pdGlhdGVkKSB7IHJldHVybiA7fVxuXG4gICAgICBpbml0aWF0ZWQgPSB0cnVlO1xuXG4gICAgICAkbW9kYWwubW9kYWwoe1xuICAgICAgICBzaG93OiBmYWxzZVxuICAgICAgfSk7XG5cbiAgICAgICRvcGVuX2J1dHRvbi5vbignY2xpY2snLCBvcGVuX3BpY2tlcik7XG4gICAgICAkcmVtb3ZlX2J1dHRvbi5vbignY2xpY2snLCByZW1vdmUpXG5cbiAgICAgIHNldF9maWVsZF9kYXRhX29uX2luaXQoKTtcbiAgICB9XG5cbiAgICBsZXQgb3Blbl9waWNrZXIgPSAoKSA9PiB7XG4gICAgICAkbW9kYWwubW9kYWwoJ3Nob3cnKTtcbiAgICAgIC8vIFRoZXNlIGhhbmRsZXJzIG11c3QgYmUgYWRkZWQgaGVyZSBiZWN1YXNlIHdlIGFyZSB1c2luZyBzYW1lIG1vZGFscyBmb3Igc2V2ZXJhbCBvcGVuZXJzXG5cbiAgICAgIC8vIEV2ZW50IGxpc3RlbmVycyBmb3IgZGF0YWJsZXMgZnJvbSBpbnNpZGUgbW9kYWxzXG4gICAgICAkbW9kYWwub24oJ3NlbGVjdC5kYXRhdGFibGUnLCAoZSwgZGF0YSkgPT4ge1xuICAgICAgICBzZXRfZmllbGRfZGF0YShkYXRhKTtcbiAgICAgIH0pO1xuICAgICAgJG1vZGFsLm9uKCdkZXNlbGVjdC5kYXRhdGFibGUnLCB1bnNldF9maWVsZF9kYXRhKTtcblxuICAgICAgJG1vZGFsLm9uKCdoaWRlLmJzLm1vZGFsJywgKCkgPT4ge1xuICAgICAgICAvLyBJbXBvcnRhbnQsIHJlbW92ZSBldmVudCBoYW5kbGVyXG4gICAgICAgICRtb2RhbC5vZmYoJ3NlbGVjdC5kYXRhdGFibGUnKTtcbiAgICAgICAgJG1vZGFsLm9mZignZGVzZWxlY3QuZGF0YXRhYmxlJyk7XG4gICAgICB9KTtcbiAgICB9XG5cbiAgICBsZXQgcmVtb3ZlID0gKCkgPT4ge1xuICAgICAgdW5zZXRfZmllbGRfZGF0YSgpO1xuICAgICAgJHJlbW92ZV9idXR0b24uYWRkQ2xhc3MoJ2Qtbm9uZScpO1xuICAgIH1cblxuICAgIGxldCBzZXRfZmllbGRfZGF0YSA9IChkYXRhKSA9PiB7XG4gICAgICAvLyBTdG9yZSBvbmx5IHZhbHVlc1xuICAgICAgbGV0IHZhbHVlID0ge1xuICAgICAgICBpZDogZGF0YS5pZCxcbiAgICAgICAgbmFtZTogZGF0YS5uYW1lLFxuICAgICAgICBsaXN0X3R5cGU6IGRhdGEubGlzdF90eXBlLFxuICAgICAgICBzb3VyY2U6IGRhdGEuc291cmNlXG4gICAgICB9XG4gICAgICB2YWx1ZSA9IEpTT04uc3RyaW5naWZ5KHZhbHVlKTtcblxuICAgICAgJGZpZWxkX2lucHV0LnZhbCh2YWx1ZSk7XG4gICAgICAkZmllbGRfaW5mby5yZW1vdmVDbGFzcygnZC1ub25lJyk7XG4gICAgICAkZmllbGRfaW5mb19uYW1lLmh0bWwoXG4gICAgICAgICdVc2luZyAnICsgJzxkaXYgY2xhc3M9XCJkLWlubGluZS1ibG9ja1wiPicgKyBkYXRhLnNvdXJjZSArICc8L2Rpdj46ICcgKyBkYXRhLm5hbWVcbiAgICAgICk7XG5cbiAgICAgICRyZW1vdmVfYnV0dG9uLnJlbW92ZUNsYXNzKCdkLW5vbmUnKTtcbiAgICB9XG5cbiAgICBsZXQgdW5zZXRfZmllbGRfZGF0YSA9IChlKSA9PiB7XG4gICAgICAkZmllbGRfaW5wdXQudmFsKCcnKTtcbiAgICAgICRmaWVsZF9pbmZvLmFkZENsYXNzKCdkLW5vbmUnKTtcbiAgICAgICRmaWVsZF9pbmZvX25hbWUuaHRtbCgnJyk7XG4gICAgfVxuXG4gICAgbGV0IHNldF9maWVsZF9kYXRhX29uX2luaXQgPSAoKSA9PiB7XG4gICAgICBpZiAoZmllbGRfaW5pdGlhbF92YWx1ZSA9PT0gJycpIHJldHVybjtcbiAgICAgIGxldCBkYXRhID0gbnVsbDtcbiAgICAgIHRyeSB7XG4gICAgICAgIGRhdGEgPSBKU09OLnBhcnNlKGZpZWxkX2luaXRpYWxfdmFsdWUpO1xuICAgICAgfSBjYXRjaChlcnJvcikge1xuICAgICAgICBjb25zb2xlLmxvZyhlcnJvcik7XG4gICAgICAgIGRhdGEgPSBudWxsO1xuICAgICAgfVxuICAgICAgaWYgKGRhdGEpIHtcbiAgICAgICAgc2V0X2ZpZWxkX2RhdGEoZGF0YSk7XG4gICAgICB9XG4gICAgfVxuICAgIC8vIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyNcblxuICAgIGluaXQoKTtcblxuICAgIHJldHVybiB0aGlzO1xuICB9O1xuXG59KCBqUXVlcnkgKSk7XG5cblxuXG4oZnVuY3Rpb24od2luZG93LCAkKSB7XG4gIGxldCBpbml0ID0gKCkgPT4ge1xuICAgIGN1c3RvbV9saXN0c19mb3JtcygpO1xuICAgIGN1c3RvbV9saXN0c19waWNrZXJzKCk7XG4gIH1cblxuICBsZXQgY3VzdG9tX2xpc3RzX2Zvcm1zID0gKCkgPT4ge1xuICAgICRjdXN0b21fbGlzdF93cmFwcGVyID0gJCgnLmpzLWN1c3RvbS1saXN0LWZvcm0td3JhcCcpO1xuICAgIGlmICgkY3VzdG9tX2xpc3Rfd3JhcHBlci5sZW5ndGggPT0gMCkgeyByZXR1cm4gfVxuXG4gICAgbGV0ICRjdXN0b21fbGlzdF9maWVsZHMgPSB7J3VzZXJuYW1lcyc6IG51bGwsICdoYXNodGFncyc6IG51bGwsICdjb21tZW50cyc6IG51bGwsICdsb2NhdGlvbnMnOiBudWxsLCAnbGlua3MnOiBudWxsfTtcbiAgICBPYmplY3Qua2V5cygkY3VzdG9tX2xpc3RfZmllbGRzKS5mb3JFYWNoKChrZXkpID0+IHtcbiAgICAgICRjdXN0b21fbGlzdF9maWVsZHNba2V5XSA9ICRjdXN0b21fbGlzdF93cmFwcGVyLmZpbmQoJy5qcy1jdXN0b20tbGlzdC0nICsga2V5KTtcbiAgICB9KTtcbiAgICAkY3VzdG9tX2xpc3RfaG9sZGVyID0gJGN1c3RvbV9saXN0X3dyYXBwZXIuZmluZCgnLmpzLWN1c3RvbS1saXN0LWhvbGRlcicpO1xuICAgICRjdXN0b21fbGlzdF9zdG9yYWdlID0gJGN1c3RvbV9saXN0X3dyYXBwZXIuZmluZCgnLmpzLWN1c3RvbS1saXN0LXN0b3JhZ2UnKTtcbiAgICAvLyAkY3VzdG9tX2xpc3RfdHlwZV9rZXkgbGlzdGVuZXJcbiAgICAkY3VzdG9tX2xpc3RfdHlwZSA9ICRjdXN0b21fbGlzdF93cmFwcGVyLmZpbmQoJy5qcy1jdXN0b20tbGlzdC10eXBlLWtleScpLmZpbmQoJ3NlbGVjdCcpO1xuICAgIGxldCBjdXN0b21fbGlzdF90eXBlX2NoYW5nZSA9IGZ1bmN0aW9uICgpIHtcbiAgICAgIHR5cGVfa2V5ID0gJGN1c3RvbV9saXN0X3R5cGUudmFsKCk7XG4gICAgICBpZiAoIXR5cGVfa2V5KSByZXR1cm47XG4gICAgICAvLyBTd2FwXG4gICAgICBjdXJyZW50X2xpc3QgPSAkY3VzdG9tX2xpc3RfaG9sZGVyLmNoaWxkcmVuKCkuYXBwZW5kVG8oJGN1c3RvbV9saXN0X3N0b3JhZ2UpO1xuICAgICAgJGN1c3RvbV9saXN0X2ZpZWxkc1t0eXBlX2tleV0uYXBwZW5kVG8oJGN1c3RvbV9saXN0X2hvbGRlcik7XG4gICAgfVxuICAgIGN1c3RvbV9saXN0X3R5cGVfY2hhbmdlKCk7XG4gICAgJGN1c3RvbV9saXN0X3R5cGUub24oJ2NoYW5nZScsIGN1c3RvbV9saXN0X3R5cGVfY2hhbmdlKTtcbiAgfVxuXG4gIGxldCBjdXN0b21fbGlzdHNfcGlja2VycyA9ICgpID0+IHtcbiAgICAkKCcuanMtY3VzdG9tLWxpc3QtcGlja2VyJykuZWFjaChmdW5jdGlvbiAoaSwgZWxlbWVudCkge1xuICAgICAgJChlbGVtZW50KS5jdXN0b21fbGlzdF9waWNrZXIoKTtcbiAgICB9KTtcbiAgfVxuXG4gIHdpbmRvdy53Q3VzdG9tTGlzdHMgPSB7XG4gICAgaW5pdCA6IGluaXRcbiAgfVxufSh3aW5kb3csIGpRdWVyeSkpOyIsIihmdW5jdGlvbih3aW5kb3csICQpIHtcblxuICBsZXQgZHluYW1pY19kYXRhdGFibGVfb3B0aW9uc19kZWZhdWx0cyA9IHtcbiAgICAvLyBwcm9wZXJ0aWVzXG4gICAgY29sdW1uczogW1xuICAgICAge1wiZGF0YVwiOlwiaWRcIn0sXG4gICAgICB7XCJkYXRhXCI6XCJuYW1lXCJ9LFxuICAgICAge1wiZGF0YVwiOlwibGlzdF90eXBlXCJ9LFxuICAgICAge1wiZGF0YVwiOlwibmFtZV9odG1sXCJ9LFxuICAgICAge1wiZGF0YVwiOlwibGlzdF90eXBlX2h0bWxcIn0sXG4gICAgICB7XCJkYXRhXCI6XCJzb3VyY2VcIn1cbiAgICBdLFxuICAgIHNlbGVjdDogdHJ1ZSxcbiAgICAvLyBldmVudHNcbiAgICBvbl9zZWxlY3Q6IChkYXRhKSA9PiB7fVxuICB9XG5cbiAgbGV0IHNldHRpbmdzID0gbnVsbDtcblxuICBsZXQgaW5pdGlhbGl6ZWQgPSAwO1xuXG4gIGxldCBpbml0ID0gKG9wdGlvbnMpID0+IHtcbiAgICBpZiAoaW5pdGlhbGl6ZWQpIHsgcmV0dXJuIH1cbiAgICBpbml0aWFsaXplZCA9IDE7XG5cbiAgICBzZXR0aW5ncyA9ICQuZXh0ZW5kKCB0cnVlLCB7fSwgZHluYW1pY19kYXRhdGFibGVfb3B0aW9uc19kZWZhdWx0cywgb3B0aW9ucyApO1xuXG4gICAgY3JlYXRlX3N0YXRpY19kYXRhdGFibGVzKCk7XG4gICAgY3JlYXRlX2R5bmFtaWNfZGF0YXRhYmxlcygpO1xuXG4gICAgcG9zdF9pbml0KCk7XG4gIH1cblxuICBsZXQgcG9zdF9pbml0ID0gKCkgPT4ge1xuICAgICQoJy5kYXRhVGFibGVzX2xlbmd0aCcpLmFkZENsYXNzKCdicy1zZWxlY3QnKTtcbiAgfVxuXG4gIGxldCBjcmVhdGVfc3RhdGljX2RhdGF0YWJsZXMgPSAoKSA9PiB7XG4gICAgJCgnLmpzLWRhdGEtdGFibGUnKS5kYXRhVGFibGUoKTtcbiAgfVxuXG4gIGxldCBjcmVhdGVfZHluYW1pY19kYXRhdGFibGVzID0gKCkgPT4ge1xuICAgIGRhdGF0YWJsZXMgPSAkKCcuanMtZGF0YS10YWJsZS1zZWxlY3QnKTtcbiAgICBkYXRhdGFibGVzLmRhdGFUYWJsZShzZXR0aW5ncyk7XG5cbiAgICBkYXRhdGFibGVzLm9uKCdzZWxlY3QuZHQnLCAoIGUsIGR0LCB0eXBlLCBpbmRleGVzICk9PiB7XG4gICAgICAkZGF0YXRhYmxlID0gJChlLnRhcmdldCk7XG4gICAgICBsZXQgZGF0YSA9IGR0LnJvd3MoaW5kZXhlcykuZGF0YSgpO1xuICAgICAgZGF0YSA9IGRhdGEgJiYgZGF0YS5sZW5ndGggPiAwID8gZGF0YVswXSA6IG51bGw7XG5cbiAgICAgIHNldHRpbmdzLm9uX3NlbGVjdC5jYWxsKG51bGwsIGRhdGEpO1xuICAgICAgJGRhdGF0YWJsZS50cmlnZ2VyKCdzZWxlY3QuZGF0YXRhYmxlJywgZGF0YSk7XG4gICAgfSk7XG5cbiAgICBkYXRhdGFibGVzLm9uKCdkZXNlbGVjdC5kdCcsICggZSwgZHQsIHR5cGUsIGluZGV4ZXMgKT0+IHtcbiAgICAgICRkYXRhdGFibGUgPSAkKGUudGFyZ2V0KTtcbiAgICAgICRkYXRhdGFibGUudHJpZ2dlcignZGVzZWxlY3QuZGF0YXRhYmxlJyk7XG4gICAgfSk7XG4gIH1cblxuICAvLyBPUFRJTUlaRTogYnVpbGQgdGFibGVzIGJ5IGxvYWRpbmcgZGF0YSBmcm9tIGJhY2tlbmRcbiAgLy8gbGV0IGdldF9kYXRhX2Zvcl9keW5hbWljX3RhYmxlcyA9ICgpID0+IHtcbiAgLy8gICAkLmdldEpTT04oJy9hcGkvZ2V0LWN1c3RvbS1saXN0cy1zb3J0ZWQtYnktbGlzdC10eXBlJylcbiAgLy8gICAgIC5kb25lKGZ1bmN0aW9uKGRhdGEpIHtcbiAgLy8gICAgICAgY3JlYXRlX2R5bmFtaWNfZGF0YXRhYmxlcyhkYXRhKTtcbiAgLy8gICAgIH0pXG4gIC8vICAgICAuZmFpbChmdW5jdGlvbigpIHtcbiAgLy8gICAgIH0pXG4gIC8vICAgICAuYWx3YXlzKGZ1bmN0aW9uKCkge1xuICAvLyAgICAgfSk7XG4gIC8vIH1cblxuICB3aW5kb3cud0RhdGFUYWJsZXMgPSB7XG4gICAgaW5pdDogaW5pdFxuICB9O1xufSh3aW5kb3csIGpRdWVyeSkpOyIsIihmdW5jdGlvbih3aW5kb3csICQpIHtcbiAgbGV0IEVtb2ppID0gY2xhc3Mge1xuICAgIGNvbnN0cnVjdG9yKCkge1xuICAgICAgLy8gUHJpdmF0ZVxuICAgICAgLy8gVGFyZ2V0cyBzaG91bGQgYmUgaW5wdXRzXG4gICAgICB0aGlzLmlucHV0X3RvX2VuYWJsZV9zZWxlY3RvciA9ICdbZGF0YS1lbW9qaWFibGUtZm9yLWVuYWJsZV0nO1xuICAgICAgdGhpcy5lZGl0b3Jfc2VsZWN0b3IgPSAnLmVtb2ppLXd5c2l3eWctZWRpdG9yJztcbiAgICAgIHRoaXMuZWxlbWVudF9hdHRyaWJ1dGVzID0ge1xuICAgICAgICAnZGF0YS1lbW9qaWFibGUnIDogJ3RydWUnLFxuICAgICAgICAnZGF0YS1lbW9qaS1pbnB1dCcgOiAndW5pY29kZSdcbiAgICAgIH07XG4gICAgICB0aGlzLmVtb2ppX3BpY2tlciA9IG5ldyBFbW9qaVBpY2tlcih7XG4gICAgICAgIGVtb2ppYWJsZV9zZWxlY3RvcjogJ1tkYXRhLWVtb2ppYWJsZT10cnVlXScsXG4gICAgICAgIGFzc2V0c1BhdGggOiAnL3N0YXRpYy9pbWcnLFxuICAgICAgICBwb3B1cEJ1dHRvbkNsYXNzZXM6ICdmYXIgZmEtc21pbGUnXG4gICAgICB9KTtcblxuICAgICAgLy8gUHVibGljXG4gICAgICB0aGlzLm9uX2Rpc2NvdmVyID0gKCkgPT4ge307XG4gICAgfVxuXG4gICAgZGlzY292ZXIocm9vdCkge1xuICAgICAgbGV0ICRyb290ID0gcm9vdCA/ICQocm9vdCkgOiBudWxsO1xuICAgICAgbGV0ICRpbnB1dF9lbGVtZW50cyA9IG51bGw7XG4gICAgICBpZiAoJHJvb3QpIHtcbiAgICAgICAgJGlucHV0X2VsZW1lbnRzID0gJHJvb3QuZmluZCh0aGlzLmlucHV0X3RvX2VuYWJsZV9zZWxlY3Rvcik7XG4gICAgICB9IGVsc2Uge1xuICAgICAgICAkaW5wdXRfZWxlbWVudHMgPSAkKHRoaXMuaW5wdXRfdG9fZW5hYmxlX3NlbGVjdG9yKTtcbiAgICAgIH1cblxuICAgICAgJGlucHV0X2VsZW1lbnRzLmF0dHIodGhpcy5lbGVtZW50X2F0dHJpYnV0ZXMpO1xuXG4gICAgICB0aGlzLmVtb2ppX3BpY2tlci5kaXNjb3ZlcigpO1xuXG4gICAgICB0aGlzLl9maXhfZWRpdG9ycygkaW5wdXRfZWxlbWVudHMpO1xuICAgIH1cblxuICAgIF9maXhfZWRpdG9ycygkaW5wdXRfZWxlbWVudHMpIHtcbiAgICAgIC8vIFRvIHRyaWdnZXIgYWRkaW5nIC5wYXJlbnQtaGFzLXNjcm9sbCBjbGFzcyBkZWZpbmVkIGluIGVtb2ppL2Vtb2ppYXJlYSBwbHVnaW5cbiAgICAgICRpbnB1dF9lbGVtZW50cy5zaWJsaW5ncyh0aGlzLmVkaXRvcl9zZWxlY3Rvcikuc2Nyb2xsKCk7XG4gICAgfVxuICB9XG5cbiAgd2luZG93LndFbW9qaSA9IEVtb2ppO1xufSh3aW5kb3csIGpRdWVyeSkpOyIsIihmdW5jdGlvbiggJCApIHtcbiAgLyoqXG4gICAqIENoYXJ0IHBsdWdpbiBqUXVlcnlcbiAgICovXG5cbiAgbGV0IG1vbnRocyA9IFtcbiAgICAnSmFudWFyeScsXG4gICAgJ0ZlYnJ1YXJ5JyxcbiAgICAnTWFyY2gnLFxuICAgICdBcHJpbCcsXG4gICAgJ01heScsXG4gICAgJ0p1bmUnLFxuICAgICdKdWx5JyxcbiAgICAnQXVndXN0JyxcbiAgICAnU2VwdGVtYmVyJyxcbiAgICAnT2N0b2JlcicsXG4gICAgJ05vdmVtYmVyJyxcbiAgICAnRGVjZW1iZXInXG4gIF07XG5cbiAgbGV0IGNoYXJ0Q29sb3JzID0ge1xuICAgIHJlZDogJ3JnYigyNTUsIDk5LCAxMzIpJyxcbiAgICBvcmFuZ2U6ICdyZ2IoMjU1LCAxNTksIDY0KScsXG4gICAgeWVsbG93OiAncmdiKDI1NSwgMjA1LCA4NiknLFxuICAgIGdyZWVuOiAncmdiKDc1LCAxOTIsIDE5MiknLFxuICAgIGJsdWU6ICdyZ2IoNTQsIDE2MiwgMjM1KScsXG4gICAgcHVycGxlOiAncmdiKDE1MywgMTAyLCAyNTUpJyxcbiAgICBncmV5OiAncmdiKDIwMSwgMjAzLCAyMDcpJ1xuICB9XG5cbiAgLy8gZW1iZWRkZWQgaW50byBjb21tb24gY29uZmlnXG4gIGxldCBjb21tb25fb3B0aW9ucyA9IHtcbiAgICByZXNwb25zaXZlOiB0cnVlLFxuICAgIGxlZ2VuZDoge1xuICAgICAgZGlzcGxheTogZmFsc2VcbiAgICB9LFxuICAgIHRpdGxlOiB7XG4gICAgICBkaXNwbGF5OiBmYWxzZVxuICAgIH0sXG4gICAgdG9vbHRpcHM6IHtcbiAgICAgIG1vZGU6ICdpbmRleCcsXG4gICAgICBpbnRlcnNlY3Q6IGZhbHNlLFxuICAgIH0sXG4gICAgaG92ZXI6IHtcbiAgICAgIGFuaW1hdGlvbkR1cmF0aW9uOiAxMDBcbiAgICB9LFxuICAgIHNjYWxlczoge1xuICAgICAgeEF4ZXM6IFt7XG4gICAgICAgIHR5cGU6ICd0aW1lJyxcbiAgICAgICAgdGltZToge1xuICAgICAgICAgIHVuaXQ6ICdkYXknXG4gICAgICAgIH0sXG4gICAgICAgIHNjYWxlTGFiZWw6IHtcbiAgICAgICAgICBkaXNwbGF5OiBmYWxzZVxuICAgICAgICB9XG4gICAgICB9XSxcbiAgICAgIHlBeGVzOiBbe1xuICAgICAgICB0aWNrczp7XG4gICAgICAgICAgYmVnaW5BdFplcm86dHJ1ZVxuICAgICAgICB9LFxuICAgICAgICB0eXBlOiAnbGluZWFyJyxcbiAgICAgICAgZGlzcGxheTogdHJ1ZSxcbiAgICAgICAgc2NhbGVMYWJlbDoge1xuICAgICAgICAgIGRpc3BsYXk6IGZhbHNlXG4gICAgICAgIH1cbiAgICAgIH1dXG4gICAgfVxuICB9O1xuXG4gIGxldCBjb21tb25fY29uZmlnID0ge1xuICAgIHR5cGU6IFwibGluZVwiLFxuICAgIG9wdGlvbnM6IGNvbW1vbl9vcHRpb25zLFxuICAgIGRhdGE6IHtcbiAgICAgIGRhdGFzZXRzOiBbe1xuICAgICAgICBsYWJlbDogJycsXG4gICAgICAgIGRhdGE6IG51bGwsXG4gICAgICAgIGZpbGw6IGZhbHNlLFxuICAgICAgICBiYWNrZ3JvdW5kQ29sb3I6IGNoYXJ0Q29sb3JzLmJsdWUsXG4gICAgICAgIGxpbmVUZW5zaW9uOiAwLFxuICAgICAgICBib3JkZXJDb2xvcjogY2hhcnRDb2xvcnMuYmx1ZSxcbiAgICAgICAgYm9yZGVyV2lkdGggOiAxXG4gICAgICB9XVxuICAgIH1cbiAgfVxuXG5cbiAgLyogUGx1Z2luIENoYXJ0ICovXG5cbiAgJC5mbi5jaGFydCA9IGZ1bmN0aW9uKG9wdGlvbnMpIHtcblxuICAgIGxldCAkc2VsZiA9ICQodGhpcyk7XG4gICAgaWYgKCRzZWxmLmxlbmd0aCAhPSAxKSB7XG4gICAgICB0aHJvdyBcIk11c3QgYmUgY2FsbGVkIG9uIG9uZSBlbGVtZW50LlwiXG4gICAgfVxuXG4gICAgbGV0IGRlZmF1bHRzID0ge1xuICAgICAgbGFiZWwgOiAnJyxcbiAgICAgIGRhdGE6IG51bGxcbiAgICB9O1xuXG4gICAgbGV0IHNldHRpbmdzID0gJC5leHRlbmQoIHRydWUsIHt9LCBkZWZhdWx0cywgb3B0aW9ucyApO1xuXG4gICAgbGV0IGluaXRpYXRlZCA9IGZhbHNlO1xuXG4gICAgbGV0ICRjaGFydCA9IG51bGw7XG4gICAgbGV0ICRjaGFydF9jYW52YXMgPSBudWxsO1xuICAgIGxldCAkY2hhcnRfY29udGV4dCA9IG51bGw7XG5cbiAgICAvLyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjXG5cbiAgICBsZXQgaW5pdCA9ICgpID0+IHtcbiAgICAgICRjaGFydF9jYW52YXMgPSAkc2VsZi5maW5kKCdjYW52YXMnKS5nZXQoMCk7XG5cbiAgICAgIC8vIEFmdGVyIHRoaXMgcG9pbnQgd2UgY2FuJ3QgY29udGludWUgaWYgaXQgd2FzIGluaXRhdGVkXG4gICAgICBpZiAoaW5pdGlhdGVkKSB7IHJldHVybiA7fVxuXG4gICAgICBjcmVhdGVfY2hhcnQoKTtcbiAgICAgIGluaXRpYXRlZCA9IHRydWU7XG4gICAgfVxuXG4gICAgbGV0IGNyZWF0ZV9jaGFydCA9ICgpID0+IHtcbiAgICAgICRjaGFydF9jb250ZXh0ID0gJGNoYXJ0X2NhbnZhcy5nZXRDb250ZXh0KCcyZCcpO1xuXG4gICAgICBsZXQgY2ZnID0gJC5leHRlbmQoIHRydWUsIHt9LCBjb21tb25fY29uZmlnLCB7XG4gICAgICAgIGRhdGE6IHtcbiAgICAgICAgICBkYXRhc2V0czogW3tcbiAgICAgICAgICAgIGxhYmVsOiBzZXR0aW5ncy5sYWJlbCxcbiAgICAgICAgICAgIGRhdGE6IHNldHRpbmdzLmRhdGFcbiAgICAgICAgICB9XVxuICAgICAgICB9XG4gICAgICB9KTtcblxuICAgICAgJGNoYXJ0ID0gbmV3IENoYXJ0KCRjaGFydF9jb250ZXh0LCBjZmcpO1xuICAgIH1cblxuICAgIC8vIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyNcblxuICAgIGluaXQoKTtcblxuICAgIHJldHVybiB0aGlzO1xuICB9O1xuXG5cblxufSggalF1ZXJ5ICkpOyIsIihmdW5jdGlvbiggJCApIHtcbiAgLyoqXG4gICAqIExpc3QgcGx1Z2luIGpRdWVyeVxuICAgKi9cbiAgJC5mbi5saXN0ID0gZnVuY3Rpb24ob3B0aW9ucykge1xuXG4gICAgbGV0ICRzZWxmID0gJCh0aGlzKTtcbiAgICBpZiAoJHNlbGYubGVuZ3RoICE9IDEpIHtcbiAgICAgIHRocm93IFwiTXVzdCBiZSBjYWxsZWQgb24gb25lIGVsZW1lbnQuXCJcbiAgICB9XG5cbiAgICBsZXQgZGVmYXVsdHMgPSB7XG4gICAgICBvbl9hZGRfaXRlbSA6ICgkaXRlbSkgPT4ge30sXG4gICAgICBzdGF0aWNfbGlzdDogZmFsc2UsXG4gICAgICBmaWx0ZXJfYnlfaW5wdXQ6IHRydWVcbiAgICB9O1xuXG4gICAgbGV0IHNldHRpbmdzID0gJC5leHRlbmQoIHRydWUsIHt9LCBkZWZhdWx0cywgb3B0aW9ucyApO1xuXG4gICAgbGV0IGluaXRpYXRlZCA9IGZhbHNlO1xuICAgIGxldCBsaXN0X2l0ZW1zX2NvdW50ID0gMDtcbiAgICBsZXQgJGxpc3RfaXRlbXMgPSBudWxsO1xuICAgIGxldCAkZmlsdGVyID0gbnVsbDtcbiAgICBsZXQgJG1ldGFkYXRhID0gbnVsbDtcbiAgICBsZXQgJHRlbXBsYXRlID0gbnVsbDtcbiAgICBsZXQgZmllbGRfbmFtZSA9IG51bGw7XG4gICAgbGV0IGxhc3RfaW5kZXggPSBudWxsO1xuXG4gICAgLy8jIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjI1xuXG4gICAgbGV0IGluaXQgPSAoKSA9PiB7XG4gICAgICAkbGlzdF9pdGVtcyA9ICRzZWxmLmZpbmQoJy5qcy1saXN0LWl0ZW1zJyk7XG4gICAgICAkZmlsdGVyID0gJHNlbGYuZmluZCgnLmpzLWxpc3QtZmlsdGVyJyk7XG4gICAgICAkbWV0YWRhdGEgPSAkc2VsZi5maW5kKCcuanMtbGlzdC1tZXRhZGF0YScpO1xuICAgICAgJHRlbXBsYXRlID0gJHNlbGYuZmluZCgnLmpzLXRlbXBsYXRlJykuY2xvbmUoKS5lcSgwKTtcbiAgICAgICRpdGVtcyA9ICRzZWxmLmZpbmQoJy5qcy1saXN0LWl0ZW0nKTtcbiAgICAgIGxpc3RfaXRlbXNfY291bnQgPSAkaXRlbXMubGVuZ3RoO1xuICAgICAgZmllbGRfbmFtZSA9ICRtZXRhZGF0YS5kYXRhKCdmaWVsZE5hbWUnKTtcbiAgICAgIGxhc3RfaW5kZXggPSBOdW1iZXIoJG1ldGFkYXRhLmRhdGEoJ2xhc3RJbmRleCcpKTtcblxuICAgICAgLy8gQWZ0ZXIgdGhpcyBwb2ludCB3ZSBjYW4ndCBjb250aW51ZSBpZiBpdCB3YXMgaW5pdGF0ZWRcbiAgICAgIGlmIChpbml0aWF0ZWQpIHsgcmV0dXJuIDt9XG5cbiAgICAgIHRvZ2dsZV9qc19saXN0X2ZpbHRlcigpO1xuICAgICAgYmluZF9ldmVudHMoKTtcbiAgICAgIGluaXRpYXRlZCA9IHRydWU7XG4gICAgfVxuXG4gICAgbGV0IHJlbW92ZV9pdGVtID0gKHJlbW92ZV9idXR0b24pID0+IHtcbiAgICAgICQocmVtb3ZlX2J1dHRvbikucGFyZW50cygnLmpzLWxpc3QtaXRlbScpLnJlbW92ZSgpO1xuICAgICAgbGlzdF9pdGVtc19jb3VudC0tO1xuICAgICAgdG9nZ2xlX2pzX2xpc3RfZmlsdGVyKCk7XG4gICAgfVxuXG4gICAgbGV0IGZpbHRlcl9saXN0ID0gKCkgPT4ge1xuICAgICAgbGV0IGZpbHRlciA9ICQodGhpcykuZmluZCgnaW5wdXQnKS52YWwoKTtcbiAgICAgIGZpbHRlcl9sb3dlcmNhc2UgPSBmaWx0ZXIudG9Mb3dlckNhc2UoKTtcblxuICAgICAgLy8gTXVzdCBiZSBmZXRjaGVkIGhlcmUgYmVjYXVzZSBvZiBuZXdseSBhZGRlZCBlbGVtZW50c1xuICAgICAgLy8gU2xpcCBpZiBsaXN0IGlzIHN0YXRpYywgaXQgd2lsbCBhbHJlYWR5IGhhdmUgYWxsIGl0ZW1zXG4gICAgICBpZiAoIXNldHRpbmdzLnN0YXRpY19saXN0KSB7XG4gICAgICAgICRpdGVtcyA9ICRzZWxmLmZpbmQoJy5qcy1saXN0LWl0ZW0nKTtcbiAgICAgIH1cblxuICAgICAgJGl0ZW1zLnNob3coKTtcblxuICAgICAgbGV0IGZpbHRlcl9mdW5jdGlvbiA9IGZ1bmN0aW9uICgpIHtcbiAgICAgICAgaWYgKHNldHRpbmdzLmZpbHRlcl9ieV9pbnB1dCkge1xuICAgICAgICAgIGZvdW5kID0gJCggdGhpcyApLnZhbCgpLnRvTG93ZXJDYXNlKCkuaW5kZXhPZiggZmlsdGVyX2xvd2VyY2FzZSApID49IDA7XG4gICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgZm91bmQgPSAkKCB0aGlzICkudGV4dCgpLnRvTG93ZXJDYXNlKCkuaW5kZXhPZiggZmlsdGVyX2xvd2VyY2FzZSApID49IDA7XG4gICAgICAgIH1cbiAgICAgICAgcmV0dXJuIGZvdW5kO1xuICAgICAgfVxuICAgICAgJGl0ZW1zLmVhY2goZnVuY3Rpb24oaSwgaXRlbSl7XG4gICAgICAgICRpdGVtID0gJChpdGVtKVxuICAgICAgICBpZiAoc2V0dGluZ3MuZmlsdGVyX2J5X2lucHV0KSB7XG4gICAgICAgICAgJGVsZW1lbnRfZm9yX2ZpbHRlcmluZyA9ICRpdGVtLmZpbmQoJ2lucHV0Jyk7XG4gICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgJGVsZW1lbnRfZm9yX2ZpbHRlcmluZyA9ICRpdGVtO1xuICAgICAgICB9XG5cbiAgICAgICAgaWYgKCEkZWxlbWVudF9mb3JfZmlsdGVyaW5nLmZpbHRlcihmaWx0ZXJfZnVuY3Rpb24pLmxlbmd0aCA+IDApIHtcbiAgICAgICAgICAkaXRlbS5oaWRlKCk7XG4gICAgICAgIH1cbiAgICAgIH0pO1xuXG4gICAgfVxuXG4gICAgbGV0IGdldF90ZW1wbGF0ZSA9ICgpID0+IHtcbiAgICAgIGxldCB0ZW1wbGF0ZSA9ICR0ZW1wbGF0ZS5jbG9uZSgpLmNoaWxkcmVuKCk7XG4gICAgICB0ZW1wbGF0ZS5maW5kKCdpbnB1dCwgc2VsZWN0LCB0ZXh0YXJlYScpLmF0dHIoJ25hbWUnLCBmaWVsZF9uYW1lICsgJy0nICsgbGFzdF9pbmRleCk7XG4gICAgICByZXR1cm4gdGVtcGxhdGU7XG4gICAgfVxuICAgIGxldCB1cGRhdGVfbGFzdF9pbmRleCA9ICgpID0+IHtcbiAgICAgIGxhc3RfaW5kZXgrKztcbiAgICAgICRtZXRhZGF0YS5kYXRhKCdsYXN0SW5kZXgnLCBsYXN0X2luZGV4KTtcbiAgICB9XG5cbiAgICBsZXQganNfbGlzdF9hZGRfaXRlbSA9ICgpID0+IHtcbiAgICAgIHVwZGF0ZV9sYXN0X2luZGV4KCk7XG4gICAgICBsZXQgJGl0ZW0gPSBnZXRfdGVtcGxhdGUoKTtcbiAgICAgICRsaXN0X2l0ZW1zLmFwcGVuZCgkaXRlbSk7XG5cbiAgICAgIGxpc3RfaXRlbXNfY291bnQrKztcbiAgICAgIHRvZ2dsZV9qc19saXN0X2ZpbHRlcigpO1xuXG4gICAgICBzZXR0aW5ncy5vbl9hZGRfaXRlbS5jYWxsKCRpdGVtLCAkaXRlbSk7XG5cbiAgICAgICRpdGVtLmZpbmQoJ2lucHV0LCB0ZXh0YXJlYScpLmZvY3VzKCk7XG4gICAgfVxuXG4gICAgbGV0IHRvZ2dsZV9qc19saXN0X2ZpbHRlciA9ICgpID0+IHtcbiAgICAgIGlmIChsaXN0X2l0ZW1zX2NvdW50ID4gMTApIHtcbiAgICAgICAgJGZpbHRlci5hZGRDbGFzcygnZC1ibG9jaycpO1xuICAgICAgfSBlbHNlIHtcbiAgICAgICAgJGZpbHRlci5yZW1vdmVDbGFzcygnZC1ibG9jaycpO1xuICAgICAgfVxuICAgIH1cblxuICAgIGxldCBiaW5kX2V2ZW50cyA9ICgpID0+IHtcbiAgICAgICRzZWxmXG4gICAgICAub24oJ2NsaWNrJywgJy5qcy1saXN0LWFjdGlvbi1hZGQnLCAoKSA9PiB7XG4gICAgICAgIGpzX2xpc3RfYWRkX2l0ZW0oKTtcbiAgICAgIH0pXG4gICAgICAub24oJ2NsaWNrJywgJy5qcy1saXN0LWFjdGlvbi1yZW1vdmUnLCAoZXZlbnQpID0+IHtcbiAgICAgICAgcmVtb3ZlX2l0ZW0oZXZlbnQudGFyZ2V0KTtcbiAgICAgIH0pXG4gICAgICAub24oJ2lucHV0JywgJy5qcy1saXN0LWZpbHRlcicsICgpID0+IHtcbiAgICAgICAgZmlsdGVyX2xpc3QoKTtcbiAgICAgIH0pXG4gICAgICAub24oJ2tleXByZXNzJywgJy5qcy1saXN0LWl0ZW0nLCAoZXZlbnQpID0+e1xuICAgICAgICB2YXIga2V5Y29kZSA9IChldmVudC5rZXlDb2RlID8gZXZlbnQua2V5Q29kZSA6IGV2ZW50LndoaWNoKTtcbiAgICAgICAgaWYgKGtleWNvZGUgPT0gMTMgJiYgIWV2ZW50LnNoaWZ0S2V5KSB7XG4gICAgICAgICAganNfbGlzdF9hZGRfaXRlbSgpO1xuICAgICAgICB9XG4gICAgICB9KTtcbiAgICB9XG4gICAgLy8jIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjI1xuXG4gICAgaW5pdCgpO1xuXG4gICAgcmV0dXJuIHRoaXM7XG4gIH07XG5cblxuXG59KCBqUXVlcnkgKSk7IiwiKGZ1bmN0aW9uKCAkICkge1xuICAvKipcbiAgICogU3VibWl0IGNvbmZpcm1hdGlvbiAkc2VsZiBwbHVnaW4galF1ZXJ5XG4gICAqL1xuICAkLmZuLnN1Ym1pdF9jb25maXJtYXRpb24gPSBmdW5jdGlvbihvcHRpb25zKSB7XG5cbiAgICBsZXQgJHNlbGYgPSAkKHRoaXMpO1xuICAgIGlmICgkc2VsZi5sZW5ndGggIT0gMSkge1xuICAgICAgdGhyb3cgXCJNdXN0IGJlIGNhbGxlZCBvbiBvbmUgZWxlbWVudC5cIlxuICAgIH1cblxuICAgIGxldCBkZWZhdWx0cyA9IHtcbiAgICAgIHRpdGxlOiAnRG91YmxlIGNoZWNrJyxcbiAgICAgIHBsYWNlbWVudDogJ2JvdHRvbSdcbiAgICB9O1xuXG4gICAgbGV0IHNldHRpbmdzID0gJC5leHRlbmQoIHRydWUsIHt9LCBkZWZhdWx0cywgb3B0aW9ucyApO1xuXG4gICAgbGV0IGluaXRpYXRlZCA9IGZhbHNlO1xuICAgIGxldCAkY29udGVudCA9IG51bGw7XG4gICAgbGV0ICRmb3JtID0gbnVsbDtcbiAgICBsZXQgJGZha2Vfc3VibWl0ID0gbnVsbDtcblxuICAgIC8vIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyNcbiAgICBsZXQgaW5pdCA9ICgpID0+IHtcbiAgICAgICRmb3JtID0gJHNlbGYucGFyZW50KCdmb3JtJyk7XG4gICAgICAkZmFrZV9zdWJtaXQgPSAkZm9ybS5maW5kKCcuanMtZmFrZS1zdWJtaXQnKTtcbiAgICAgICRjb250ZW50ID0gJHNlbGYuY2hpbGRyZW4oKS5lcSgwKTtcblxuICAgICAgLy8gQWZ0ZXIgdGhpcyBwb2ludCB3ZSBjYW4ndCBjb250aW51ZSBpZiBpdCB3YXMgaW5pdGF0ZWRcbiAgICAgIGlmIChpbml0aWF0ZWQpIHsgcmV0dXJuIDt9XG5cbiAgICAgIGNyZWF0ZV9wb3BvdmVyKCk7XG4gICAgICBiaW5kX2V2ZW50cygpO1xuICAgICAgaW5pdGlhdGVkID0gdHJ1ZTtcbiAgICB9XG5cbiAgICBsZXQgYmluZF9ldmVudHMgPSAoKSA9PiB7XG4gICAgICAkY29udGVudFxuICAgICAgLm9uKCdjbGljaycsICdidXR0b24nLCAoKSA9PiB7XG4gICAgICAgICRmb3JtLnN1Ym1pdCgpO1xuICAgICAgfSk7XG4gICAgfVxuXG4gICAgbGV0IGNyZWF0ZV9wb3BvdmVyID0gKCkgPT4ge1xuICAgICAgaWYgKCRmYWtlX3N1Ym1pdC5sZW5ndGggPT0gMClcbiAgICAgICAgcmV0dXJuO1xuXG4gICAgICAkZmFrZV9zdWJtaXQucG9wb3Zlcih7XG4gICAgICAgIHRpdGxlOiBzZXR0aW5ncy50aXRsZSxcbiAgICAgICAgdHJpZ2dlcjogJ2ZvY3VzJyxcbiAgICAgICAgaHRtbDogdHJ1ZSxcbiAgICAgICAgY29udGVudDogJGNvbnRlbnQsXG4gICAgICAgIHBsYWNlbWVudDogc2V0dGluZ3MucGxhY2VtZW50XG4gICAgICB9KTtcbiAgICB9XG5cbiAgICAvLyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjXG5cbiAgICBpbml0KCk7XG5cbiAgICByZXR1cm4gdGhpcztcbiAgIH07XG5cbiB9KCBqUXVlcnkgKSk7XG4iLCJcbihmdW5jdGlvbiggJCApIHtcbiQoKCkgPT4ge1xuICAoKCkgPT4ge1xuICB9KSgpO1xuXG4gIC8vIGRpZG4ndCBsaWtlIGl0IC0gQW5pbWF0aW9ucyBpbml0aWFsaXphdGlvblxuICAvL25ldyBXT1coKS5pbml0KCk7XG5cbiAgbGV0IGVtb2ppID0gbmV3IHdFbW9qaSgpO1xuXG4gIC8vIEluaXRpYWxpc2UgbGlzdHNcbiAgJCgnLmpzLWxpc3QnKS5lYWNoKGZ1bmN0aW9uIChpLCBlbGVtZW50KSB7XG4gICAgJChlbGVtZW50KS5saXN0KHtcbiAgICAgIG9uX2FkZF9pdGVtOiAoJGl0ZW0pID0+IHtcbiAgICAgICAgZW1vamkuZGlzY292ZXIoJGl0ZW0pO1xuICAgICAgfVxuICAgIH0pO1xuICB9KTtcblxuICAkKCcuanMtbGlzdC1zdGF0aWMnKS5lYWNoKGZ1bmN0aW9uIChpLCBlbGVtZW50KSB7XG4gICAgJChlbGVtZW50KS5saXN0KHtcbiAgICAgIHN0YXRpY19saXN0OiB0cnVlLFxuICAgICAgZmlsdGVyX2J5X2lucHV0OiBmYWxzZVxuICAgIH0pO1xuICB9KTtcblxuICAvLyBEb3VibGUgY2hlY2sgcG9wdXBzIGZvciBzdWJtaXR0aW5nIGZvcm1zXG4gICQoJy5qcy1zdWJtaXQtY29uZmlybWF0aW9uLXBvcG92ZXInKS5lYWNoKChpLCBlbGVtZW50KSA9PiB7XG4gICAgJChlbGVtZW50KS5zdWJtaXRfY29uZmlybWF0aW9uKCk7XG4gIH0pO1xuXG4gIC8vIEZvcm0gdmFsaWRhdGlvbiAtIGp1c3QgcmVxdWlyZWQgZmllbGRzXG4gICQoJ2Zvcm0nKS5zdWJtaXQoZnVuY3Rpb24oKXtcbiAgICBsZXQgJGZvcm0gPSAkKHRoaXMpO1xuICAgIGxldCB2YWxpZCA9IHRydWU7XG4gICAgJGZvcm0uZmluZCgnW3JlcXVpcmVkXScpLmVhY2goZnVuY3Rpb24oKSB7XG4gICAgICAgIGxldCAkZXJyb3JzID0gJCh0aGlzKS5zaWJsaW5ncygnLmpzLWVycm9ycycpO1xuICAgICAgICBpZiAoJCh0aGlzKS52YWwoKSA9PT0gJycpIHtcbiAgICAgICAgICB2YWxpZCA9IGZhbHNlO1xuICAgICAgICAgICRlcnJvcnMudGV4dCgnUmVxdWlyZWQnKTtcbiAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAkZXJyb3JzLnRleHQoJycpO1xuICAgICAgICB9XG4gICAgfSk7XG4gICAgcmV0dXJuIHZhbGlkO1xuICB9KTtcblxuICAvLyBUaGlzIGlzIGZvciBmb3JtIHN1Ym1pdHMgdGhhdCBhcmUgb3V0c2lkZSBvZiB0aGUgZm9ybXMgdGhleSBuZWVkIHRvIHN1Ym1pdFxuICAkKCdbZGF0YS1mb3JtLXRvLXN1Ym1pdF0nKS5jbGljayhmdW5jdGlvbiAoKSB7XG4gICAgbGV0IGZvcm1faWQgPSAkKHRoaXMpLmRhdGEoJ2Zvcm1Ub1N1Ym1pdCcpO1xuICAgIGxldCBhZGRpdGlvbmFsX3F1ZXJ5X3BhcmFtcyA9ICQodGhpcykuZGF0YSgnYWRkaXRpb25hbFF1ZXJ5UGFyYW1zJyk7XG4gICAgbGV0ICRmb3JtID0gJCgnLicgKyBmb3JtX2lkKTtcbiAgICBpZiAoISRmb3JtLmxlbmd0aCkge1xuICAgICAgIHJldHVybjtcbiAgICB9XG5cbiAgICBpZiAoYWRkaXRpb25hbF9xdWVyeV9wYXJhbXMpIHtcbiAgICAgIGFkZGl0aW9uYWxfcXVlcnlfcGFyYW1zID0gYWRkaXRpb25hbF9xdWVyeV9wYXJhbXMucmVwbGFjZSgvJy9nLCAnXCInKTtcbiAgICAgIGFkZGl0aW9uYWxfcXVlcnlfcGFyYW1zID0gSlNPTi5wYXJzZShhZGRpdGlvbmFsX3F1ZXJ5X3BhcmFtcyk7XG4gICAgICAvLyBsZXQgYWN0aW9uID0gJGZvcm0uYXR0cignYWN0aW9uJyk7XG4gICAgICAvLyBpZiAoYWN0aW9uLmluZGV4T2YoJz8nKSA9PSAtMSkge1xuICAgICAgLy8gICAgIGFjdGlvbiArPSAnPyc7XG4gICAgICAvLyB9XG4gICAgICAvLyAvLyBBZGQgJiBpZiBpdCBoYXMgbW9yZSBwYXJhbXNcbiAgICAgIC8vIGlmIChhY3Rpb24uc3Vic3RyKC0xKSAhPSAnPycpIHtcbiAgICAgIC8vICAgYWN0aW9uICs9ICcmJztcbiAgICAgIC8vIH1cbiAgICAgIC8vIGFjdGlvbiA9IGFjdGlvbiArICQucGFyYW0oYWRkaXRpb25hbF9xdWVyeV9wYXJhbXMpO1xuICAgICAgT2JqZWN0LmtleXMoYWRkaXRpb25hbF9xdWVyeV9wYXJhbXMpLmZvckVhY2goZnVuY3Rpb24oa2V5KSB7XG4gICAgICAgIGxldCB2YWx1ZSA9IGFkZGl0aW9uYWxfcXVlcnlfcGFyYW1zW2tleV07XG4gICAgICAgIHZhciAkaW5wdXQgPSAkKCc8aW5wdXQgdHlwZT1cImhpZGRlblwiIC8+JylcbiAgICAgICAgJGlucHV0LmF0dHIoJ25hbWUnLCBrZXkpO1xuICAgICAgICAkaW5wdXQudmFsKHZhbHVlKTtcbiAgICAgICAgJGZvcm0uYXBwZW5kKCRpbnB1dCk7XG4gICAgICB9KTtcbiAgICAgIC8vICRmb3JtLmF0dHIoJ2FjdGlvbicsIGFjdGlvbik7XG4gICAgfVxuICAgICRmb3JtLnN1Ym1pdCgpO1xuICB9KTtcblxuICAvLyBTZXNzaW9uIHNldHRpbmdzIGxpc3RlbmVyXG4gICQoJy5qcy1zZXNzaW9uLXNldHRpbmdzLWFjdGlvbi1saXN0ZW5lcicpXG4gICAgLm9uKCdjbGljaycsICcuanMtc2V0dGluZ3MtYWN0aW9uLWlucHV0LWhlbHAnLCBmdW5jdGlvbigpIHtcbiAgICAgIC8vIFRvIGVuYWJsZSBpbnB1dCBoZWxwZXJzXG4gICAgICBsZXQgdmFsdWUgPSAkKHRoaXMpLmRhdGEoJ3ZhbHVlJyk7XG5cbiAgICAgICQodGhpcykucGFyZW50cygnLmpzLXNldHRpbmdzLWVsZW1lbnQtaW5wdXQtcGFyZW50JykuZmluZCgnaW5wdXQnKVxuICAgICAgICAuZm9jdXMoKVxuICAgICAgICAudmFsKHZhbHVlKTtcbiAgICAgIHJldHVybiBmYWxzZTtcbiAgICB9KTtcblxuICAvLyBTZXR0aW5ncyBpbmZvIGNvbGxhcHNpYmxlc1xuICBsZXQgc2V0dGluZ3NfY29sbGFwc2VfbGFzdF9zdGF0ZSA9ICdoaWRlJztcbiAgJGNvbGxhcHNpYmxlc190b19za2lwID0gJCgnbmF2IC5jb2xsYXBzZScpO1xuICAkY29sbGFwc2libGVzID0gJCgnLmNvbGxhcHNlJykubm90KCRjb2xsYXBzaWJsZXNfdG9fc2tpcCk7XG4gICQoJy5qcy1hY3Rpb24tdG9nZ2xlLWFsbC1zZXR0aW5ncy1oZWxwJykub24oJ2NsaWNrJywgZnVuY3Rpb24oKSB7XG4gICAgaWYgKHNldHRpbmdzX2NvbGxhcHNlX2xhc3Rfc3RhdGUgPT09ICdoaWRlJykge1xuICAgICAgJGNvbGxhcHNpYmxlcy5jb2xsYXBzZSgnc2hvdycpO1xuICAgICAgc2V0dGluZ3NfY29sbGFwc2VfbGFzdF9zdGF0ZSA9J3Nob3cnO1xuICAgIH0gZWxzZSB7XG4gICAgICAkY29sbGFwc2libGVzLmNvbGxhcHNlKCdoaWRlJyk7XG4gICAgICBzZXR0aW5nc19jb2xsYXBzZV9sYXN0X3N0YXRlID0naGlkZSc7XG4gICAgfVxuICB9KTtcblxuICAvLyBUb2dnbGUgZGlzcGxheWVkIHNldHRpbmdzIGZvciBkaWZmZXJlbnQgbW9kZXM6IHNpbXBsZSwgYWR2YW5jZWQsIGV4cGVydFxuICB2aXNpYmlsaXR5X3RvZ2dsZWRfZWxlbWVudHMgPSAkKCcuanMtdmlzaWJpbGl0eS10b2dnbGUnKTtcbiAgdmlzaWJpbGl0eV90b2dnbGVkX2VsZW1lbnRzX2FkdmFuY2VkID0gdmlzaWJpbGl0eV90b2dnbGVkX2VsZW1lbnRzLmZpbHRlcignLmpzLWFkdmFuY2VkJyk7XG4gIHZpc2liaWxpdHlfdG9nZ2xlZF9lbGVtZW50c19leHBlcnQgPSB2aXNpYmlsaXR5X3RvZ2dsZWRfZWxlbWVudHMuZmlsdGVyKCcuanMtZXhwZXJ0Jyk7XG4gICQoJy5qcy1hY3Rpb24tY2hhbmdlLXNldHRpbmdzLXZpZXctbGV2ZWwnKS5vbignY2xpY2snLCAnYScsIGZ1bmN0aW9uKGUpIHtcbiAgICBhbmNob3IgPSAkKHRoaXMpO1xuICAgIGxldmVsID0gYW5jaG9yLmRhdGEoJ2xldmVsJyk7XG4gICAgLy8gc2V0IHVwIGFjdGl2ZSBjbGFzcyBvbiBjb3JyZWN0IGVsZW1lbnRcbiAgICBhbmNob3Iuc2libGluZ3MoKS5yZW1vdmVDbGFzcygnYWN0aXZlJylcbiAgICBhbmNob3IuYWRkQ2xhc3MoJ2FjdGl2ZScpO1xuXG4gICAgaWYgKGxldmVsID09PSAnZXhwZXJ0Jykge1xuICAgICAgdmlzaWJpbGl0eV90b2dnbGVkX2VsZW1lbnRzLnJlbW92ZUNsYXNzKCdkLW5vbmUnKTtcbiAgICB9IGVsc2UgaWYgKGxldmVsID09PSAnYWR2YW5jZWQnKSB7XG4gICAgICB2aXNpYmlsaXR5X3RvZ2dsZWRfZWxlbWVudHNfZXhwZXJ0LmFkZENsYXNzKCdkLW5vbmUnKTtcbiAgICAgIHZpc2liaWxpdHlfdG9nZ2xlZF9lbGVtZW50c19hZHZhbmNlZC5yZW1vdmVDbGFzcygnZC1ub25lJyk7XG4gICAgfSBlbHNlIHtcbiAgICAgIHZpc2liaWxpdHlfdG9nZ2xlZF9lbGVtZW50cy5hZGRDbGFzcygnZC1ub25lJyk7XG4gICAgfVxuXG4gICAgLy8gZGlzYWJsZSBsaW5rXG4gICAgZS5wcmV2ZW50RGVmYXVsdCgpO1xuICB9KTtcblxuICAvLyBQcm9maWxlIGZpbHRlciBpbiBuYXZpZ2F0aW9uIGJhclxuICAkKCcuanMtbmF2LXByb2ZpbGUtbGlzdCcpXG4gIC5vbignaW5wdXQnLCAnaW5wdXQnLCBmdW5jdGlvbigpIHtcbiAgICBsZXQgcGFyZW50ID0gJCh0aGlzKS5wYXJlbnRzKCcuanMtbmF2LXByb2ZpbGUtbGlzdCcpO1xuICAgIGxldCBmaWx0ZXIgPSAkKHRoaXMpLnZhbCgpO1xuICAgIGZpbHRlcl9sb3dlcmNhc2UgPSBmaWx0ZXIudG9Mb3dlckNhc2UoKTtcblxuICAgIHByb2ZpbGVfaXRlbXMgPSBwYXJlbnQuZmluZCgnLmpzLW5hdi1wcm9maWxlLWxpc3QtaXRlbScpO1xuICAgIHByb2ZpbGVfaXRlbXMuc2hvdygpO1xuXG4gICAgbGV0IGZpbHRlcl9mdW5jdGlvbiA9IGZ1bmN0aW9uICgpIHtcbiAgICAgIHJldHVybiAkKCB0aGlzICkudGV4dCgpLnRvTG93ZXJDYXNlKCkuaW5kZXhPZiggZmlsdGVyX2xvd2VyY2FzZSApID49IDA7XG4gICAgfVxuICAgIHByb2ZpbGVfaXRlbXMuZWFjaChmdW5jdGlvbihpLCBwcm9maWxlX2l0ZW0pe1xuICAgICAgcHJvZmlsZV9pdGVtID0gJChwcm9maWxlX2l0ZW0pO1xuICAgICAgcHJvZmlsZV9pdGVtX25hbWUgPSBwcm9maWxlX2l0ZW0uZmluZCgnLm5hdi10ZXh0OmZpcnN0Jyk7XG4gICAgICBpZiAoIXByb2ZpbGVfaXRlbV9uYW1lLmZpbHRlcihmaWx0ZXJfZnVuY3Rpb24pLmxlbmd0aCA+IDApIHtcbiAgICAgICAgcHJvZmlsZV9pdGVtLmhpZGUoKTtcbiAgICAgIH1cbiAgICB9KTtcblxuICAgIHJldHVybiBmYWxzZTtcbiAgfSk7XG5cbiAgLy8gUGFzc3dvcmQgZmllbGQgaXMgaGlkZGVuIG9uIHByb2ZpbGUgc2V0dGluZ3MgcGFnZVxuICAkKCcuanMtcmV2ZWFsLXBhc3N3b3JkLWZpZWxkJykub24oJ2NsaWNrJywgZnVuY3Rpb24oKSB7XG4gICAgJCh0aGlzKS5hZGRDbGFzcygnZC1ub25lJyk7XG4gICAgJCgnLmpzLWhpZGRlbi1wYXNzd29yZC1maWVsZCcpLnJlbW92ZUNsYXNzKCdkLW5vbmUnKTtcbiAgfSk7XG5cblxuXG4gIC8vIEFuaW1hdGlvbiB3aGVuIGxvYWRpbmcgYW5kIHVubG9hZGluZyB0aGUgc2l0ZVxuICBsZXQgcGFnZV9sb2FkZXIgPSAkKCcuanMtcGFnZS1sb2FkZXInKTtcbiAgcGFnZV9sb2FkZXIuYWRkQ2xhc3MoJ2Qtbm9uZScpO1xuICAkKHdpbmRvdykub24oXCJiZWZvcmV1bmxvYWRcIiwgZnVuY3Rpb24oZXZlbnQpIHtcbiAgICBwYWdlX2xvYWRlci5yZW1vdmVDbGFzcygnZC1ub25lJyk7XG4gIH0pO1xuXG4gIC8vIEZvbGxvd2VyIEZvbGxvd2luZyB0b29sXG4gICRmb2xsb3dfZm9sbG93aW5nX3Rvb2wgPSAkKCcuanMtZm9sbG93ZXItZm9sbG93aW5nLXRvb2wtY3JlYXRlLXJlcXVlc3QnKTtcbiAgJGZvbGxvd19mb2xsb3dpbmdfdG9vbF91bmZvbGxvd2Vyc19maWVsZHMgPSAkKCcuanMtZm9sbG93ZXJfZm9sbG93aW5nX3Rvb2xfdW5mb2xsb3dlcnNfZmllbGRzJyk7XG4gIGlmICgkZm9sbG93X2ZvbGxvd2luZ190b29sLmxlbmd0aCA+IDApIHtcbiAgICAkZm9sbG93X2ZvbGxvd2luZ190b29sLmZpbmQoJy5qcy1mb2xsb3dlcl9mb2xsb3dpbmdfdG9vbF90eXBlJylcbiAgICAgIC5maW5kKCdzZWxlY3QnKS5vbignY2hhbmdlJywgZnVuY3Rpb24oKSB7XG4gICAgICAgIHZhbHVlID0gdGhpcy52YWx1ZTtcbiAgICAgICAgJGZvbGxvd19mb2xsb3dpbmdfdG9vbF91bmZvbGxvd2Vyc19maWVsZHNcbiAgICAgICAgICAuYWRkQ2xhc3MoJ2Qtbm9uZScpO1xuICAgICAgICBpZiAodmFsdWUuaW5kZXhPZigndW5mb2xsb3cnKSA+IC0xKSB7XG4gICAgICAgICAgJGZvbGxvd19mb2xsb3dpbmdfdG9vbF91bmZvbGxvd2Vyc19maWVsZHNcbiAgICAgICAgICAgIC5yZW1vdmVDbGFzcygnZC1ub25lJyk7XG4gICAgICAgIH1cbiAgICAgIH0pO1xuICB9XG5cbiAgLy8gRGF0YVRhYmxlc1xuICB3RGF0YVRhYmxlcy5pbml0KCk7XG5cbiAgLy8gQ3VzdG9tTGlzdHNcbiAgd0N1c3RvbUxpc3RzLmluaXQoKTtcblxuICAvLyBMZXQncyBjYWxsIHRoaXMgbGFzdFxuICAvLyBIYXMgdG8gYmUgY2FsbGVkIGFmdGVyIGluaXRpYWxpc2luZyBsaXN0IGJlY2F1c2Ugb2YgdGhlIGxpc3QgdGVtcGxhdGVzXG4gIGVtb2ppLmRpc2NvdmVyKCk7XG5cbiAgLy8gSW1wb3J0YW50XG4gIGNvbnNvbGUubG9nKC8qYXRvYigqLydWR2x6SUhSeWRXVWdkMmwwYUc5MWRDQnNlV2x1Wnl3Z1kyVnlkR0ZwYmlCaGJtUWdiVzl6ZENCMGNuVmxMaUJVYUdGMElIZG9hV05vSUdseklHSmxiRzkzSUdseklHeHBhMlVnZEdoaGRDQjNhR2xqYUNCcGN5QmhZbTkyWlNCaGJtUWdkR2hoZENCM2FHbGphQ0JwY3lCaFltOTJaU0JwY3lCc2FXdGxJSFJvWVhRZ2QyaHBZMmdnYVhNZ1ltVnNiM2NnZEc4Z1pHOGdkR2hsSUcxcGNtRmpiR1Z6SUc5bUlHOXVaU0J2Ym14NUlIUm9hVzVuTGlBZ0xTQlVhR1VnUlcxbGNtRnNaQ0JVWVdKc1pYUT0nLyopKi8pXG59KTtcbn0oalF1ZXJ5KSk7Il19
