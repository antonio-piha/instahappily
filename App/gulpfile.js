'use strict';

var gulp = require('gulp');
var sass = require('gulp-sass');
var postcss = require('gulp-postcss');
var minifyCSS = require('gulp-csso');
var sourcemaps = require('gulp-sourcemaps');
var autoprefixer = require('autoprefixer');
var concat = require('gulp-concat');
var merge = require('merge-stream');

// For further theming
// gulp.task('sass-theme', () => {
//   return gulp.src(['./scss/theme.scss'])
//     .pipe(sass().on('error', sass.logError))
//     .pipe(gulp.dest('./static'));
// });

// gulp.task('css-theme', () => {
//   return gulp.src('./static/theme.css')
//     .pipe(postcss([ autoprefixer() ]))
//     .pipe(minifyCSS())
//     .pipe(gulp.dest('./static'));
// });

gulp.task('libs', () => {
  let libjs = gulp.src([
    'node_modules/jquery/dist/jquery.min.js',
    'node_modules/mdbootstrap/js/popper.min.js',
    'node_modules/mdbootstrap/js/bootstrap.min.js',
    'node_modules/mdbootstrap/js/mdb.min.js',
    // Addons
    'node_modules/mdbootstrap/js/addons/datatables.min.js',
    'node_modules/mdbootstrap/js/addons/datatables-select.min.js',
    'node_modules/moment/min/moment-with-locales.min.js',
    'node_modules/chart.js/dist/Chart.min.js',
    'frontend-third-parties/onesignal-emoji-picker/lib/js/config.js',
    'frontend-third-parties/onesignal-emoji-picker/lib/js/util.js',
    'frontend-third-parties/onesignal-emoji-picker/lib/js/jquery.emojiarea.js',
    'frontend-third-parties/onesignal-emoji-picker/lib/js/emoji-picker.js',
  ])
    .pipe(concat('lib.js'))
    .pipe(gulp.dest('./static/js'));

  let css = gulp.src([
    'node_modules/@fortawesome/fontawesome-free/css/all.min.css',
    'node_modules/mdbootstrap/css/bootstrap.min.css',
    'node_modules/mdbootstrap/css/mdb.min.css',
    'node_modules/mdbootstrap/css/addons/datatables.min.css',
    'node_modules/mdbootstrap/css/addons/datatables-select.min.css',
    'node_modules/mdbootstrap/css/addons/directives.min.css',
    'frontend-third-parties/onesignal-emoji-picker/lib/css/emoji.css',
  ])
    .pipe(concat('theme.css'))
    .pipe(gulp.dest('./static/css'));

  let font_awesome = gulp.src('node_modules/@fortawesome/fontawesome-free/webfonts/*', { base: 'node_modules/@fortawesome/fontawesome-free/webfonts' })
    .pipe(gulp.dest('./static/webfonts'));

  let mdb_font = gulp.src('node_modules/mdbootstrap/font/**/*', { base: 'node_modules/mdbootstrap/font' })
    .pipe(gulp.dest('./static/font'));

  let emoji_picker = gulp.src('frontend-third-parties/onesignal-emoji-picker/lib/img/*', { base: 'frontend-third-parties/onesignal-emoji-picker/lib/img' })
    .pipe(gulp.dest('./static/img'));

  let images = gulp.src('image/*', { base: 'image' })
    .pipe(gulp.dest('./static/img'));

  return merge(libjs, css, font_awesome, mdb_font, emoji_picker, images);
});


gulp.task('app-css', () => {
  let compile = gulp.src(['./scss/*.scss'])
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest('./static/css'));

  let minify = gulp.src('./static/app.css')
    .pipe(sourcemaps.init())
    .pipe(minifyCSS())
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest('./static/css'));

  return merge(compile, minify);
});

gulp.task('app-js', () => {
  return gulp.src([
    'js/!(app)*.js',
    'js/app.js',
  ])
    .pipe(sourcemaps.init())
    .pipe(concat('app.js'))
    .pipe(sourcemaps.write())
    .pipe(gulp.dest('./static/js'));
});

gulp.task('default', ['app-css', 'app-js'], () => {
  gulp.watch('./scss/*.scss', ['app-css']);
  gulp.watch('./js/*.js', ['app-js'])
});