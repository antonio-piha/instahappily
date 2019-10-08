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