module.exports = function(grunt) {

  // Initializing the configuration object
  grunt.initConfig({

    less: {
      development: {
        options: {
          compress: false // true
        },
        files: {
          "./webapp/static/dist/kla.css": "./webapp/static/less/kla.less"
        }
      }
    },

    copy: {
      main: {
        files: [
          {
            expand: true,
            cwd: 'bower_components/',
            src: [
              'bootstrap/dist/js/bootstrap.min.js',
              'bootstrap/dist/fonts/**',
              // 'jquery/dist/jquery.min.js',
              'jquery/dist/jquery.js',  // for dev
              'jquery/dist/jquery.min.map',
              'jquery-ui/jquery-ui.min.js',
              'jquery-ui/themes/smoothness/jquery-ui.min.css',
              'font-awesome/fonts/**',
              //'jsTree/dist/jstree.min.js'
              'jsTree/dist/jstree.js',  // for dev
              'datetimepicker/jquery.datetimepicker.css',
              'datetimepicker/jquery.datetimepicker.js'
            ],
            dest: './webapp/static/dist/',
            filter: 'isFile',
            flatten: true
          },
          {
            expand: true,
            cwd: 'webapp/static/js/',
            src: [
              'kla.js',
            ],
            dest: './webapp/static/dist/',
            filter: 'isFile',
            flatten: true
          }
        ]
      }
    },

    clean: ['./webapp/static/dist'],

    watch: {
      less: {
        files: ['./webapp/static/less/*.less'], //watched files
        tasks: ['less'], //tasks to run
        options: {
          livereload: true
        }
      },
      js: {
        files: ['./webapp/static/js/*.js'], //watched files
        tasks: ['copy'], //tasks to run
        options: {
          livereload: true
        }
      }
    }
  });

  // Plugin loading
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-less');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-clean');

  // Task definition
  grunt.registerTask('build', ['copy', 'less']);
  grunt.registerTask('default', ['build', 'watch']);
};