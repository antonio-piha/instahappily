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