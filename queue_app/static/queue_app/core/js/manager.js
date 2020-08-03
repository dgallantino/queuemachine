var handle_call = function(event){
	event.preventDefault();
	$(this).progressInitialize();

	var defaults = {
			is_called : "True",
			url_location : "href",
			booth_locatian : "session_booth",
			sound_obj : $(event.target).closest('a').siblings('.call-audio')[0],
	};
	$.extend(defaults, event.data);

	if ($(event.target).closest('tr').hasClass('called')){
		var call_audio = $(event.target).siblings('.call-audio')[0] || defaults.sound_obj;
		if (call_audio.paused){
			call_audio.currentTime=0;
			call_audio.play();
		}else{
			call_audio.pause();
		}
		return false;
	}


	//POST request before actualy calling the queue
	var call_url = $(this).attr('href') || $(this).attr(defaults.url_locatian);
	var session_booth = $(this).attr('session_booth') || $(this).attr(defaults.booth_locatian);
	var form_data = "is_called="+defaults.is_called+"&counter_booth="+session_booth;
	if (!session_booth){
		var error_message = "System Err:\n";
		error_message += "[403] : Please choose your counter / desk first";
		window.alert(error_message);
		return false;
	}
	$.ajax({
		url : call_url,
		type : "POST",
		dataType: 'html',
		contentType: 'application/x-www-form-urlencoded',
		data:form_data,
	})
	.fail(function(xhr){
		var error_message = "AJAX Err:\n";
		error_message += "["+xhr.status.toString()+"] : ";
		error_message += xhr.statusText;
		window.alert(error_message);
	})
	.done(function(data){
		$(event.target).closest('tr').addClass('called');
	});
	return false;
};

const handle_finish = function (event) {
	event.preventDefault();
	console.log('test');
	var post_url = $(this).attr('href')
	var form_data = "is_finished=True"
	$.ajax({
		url : post_url,
		type : 'POST',
		dataType : 'html',
		contentType : 'application/x-www-form-urlencoded',
		data : form_data,
	})
	.fail(function (xhr) {
		var error_message = "AJAX Err:\n";
		error_message += "["+xhr.status.toString()+"] : ";
		error_message += xhr.statusText;
		window.alert(error_message);
	})
	.done(function (data) {
		$(event.target).closest('.called').remove()
	})

};

var audio_progress = function(audio_obj){
	var ctrl_button = $(audio_obj).siblings('a.progress-button');
	var time_max = audio_obj.duration;
	ctrl_button.progressSet((audio_obj.currentTime/audio_obj.duration)*100);
};

(function($){
	$.fn.initiate_dropdown = function(){
		$.each(this,function(idx,dom_obj){
			var $this = $(dom_obj);
			var booth_url = $this.attr('href')||$this.attr('url_data');
			$.ajax({
					url : booth_url,
					type : "GET",
					dataType: 'html',
				})
				.fail(function(xhr){
					var error_message = "AJAX Err:\n";
					error_message += "["+xhr.status.toString()+"] : ";
					error_message += xhr.statusText;
					window.alert(error_message);
				})
				.done(function(data){
					$this.html(data);
				});
		});
		return this;
	};

	//request the most updated queue list
	$.fn.as_queue_list = function(){
		$.each(this,function(idx,dom_obj){
			var queue_url = $(dom_obj).attr('queues_url');
			var loading_html =	'<tr><td class ="text-center" colspan="5">';
			loading_html += '<i class="fa fa-spinner fa-pulse fa-3x fa-fw"></i>';
			loading_html += '<span class="sr-only">Loading...</span>';
			loading_html += '</td></tr>';
			$(dom_obj).html(loading_html);
			$.ajax({
				url:queue_url,
				type:'GET',
				dataType:'html',
				contentType: 'application/x-www-form-urlencoded',
			})
			.fail(function(xhr){
				window.alert(xhr.status.toString());
			})
			.done(function(response){
				$(dom_obj).html(response);
			});
		});
		return this;
	};

    // Creating a number of jQuery plugins that you can use to
    // initialize and control the progress meters.

    $.fn.progressInitialize = function(){

        // This function creates the necessary markup for the progress meter
        // and sets up a few event listeners.

        // Loop through all the buttons:

        return this.each(function(){

            var button = $(this),
                progress = 0;

            // Extract the data attributes into the options object.
            // If they are missing, they will receive default values.

            var options = $.extend({
                type:'background-horizontal',
                loading: 'Loading..',
                finished: 'Done!'
            }, button.data());

            // Add the data attributes if they are missing from the element.
            // They are used by our CSS code to show the messages
            button.attr({'data-loading': options.loading, 'data-finished': options.finished});

            // Add the needed markup for the progress bar to the button
            var bar = $('<span class="tz-bar ' + options.type + '">').appendTo(button);

            // The progress event tells the button to update the progress bar
            button.on('progress', function(e, val, absolute, finish){

                if(!button.hasClass('in-progress')){

                    // This is the first progress event for the button (or the
                    // first after it has finished in a previous run). Re-initialize
                    // the progress and remove some classes that may be left.

                    bar.show();
                    progress = 0;
                    button.removeClass('finished').addClass('in-progress')
                }

                // val, absolute and finish are event data passed by the progressIncrement
                // and progressSet methods that you can see near the end of this file.

                if(absolute){
                    progress = val;
                }
                else{
                    progress += val;
                }

                if(progress >= 100){
                    progress = 100;
                }

                if(finish){

                    button.removeClass('in-progress').addClass('finished');

                    bar.delay(500).fadeOut(function(){

                        // Trigger the custom progress-finish event
                        button.trigger('progress-finish');
                        setProgress(0);
                    });

                }

                setProgress(progress);
            });

            function setProgress(percentage){
                bar.filter('.background-horizontal,.background-bar').width(percentage+'%');
                bar.filter('.background-vertical').height(percentage+'%');
            }

        });

    };

    // progressStart simulates activity on the progress meter. Call it first,
    // if the progress is going to take a long time to finish.

    $.fn.progressStart = function(){

        var button = this.first(),
            last_progress = new Date().getTime();

        if(button.hasClass('in-progress')){
            // Don't start it a second time!
            return this;
        }

        button.on('progress', function(){
            last_progress = new Date().getTime();
        });

        // Every half a second check whether the progress
        // has been incremented in the last two seconds

        var interval = window.setInterval(function(){

            if( new Date().getTime() > 2000+last_progress){

                // There has been no activity for two seconds. Increment the progress
                // bar a little bit to show that something is happening

                button.progressIncrement(5);
            }

        }, 500);

        button.on('progress-finish',function(){
            window.clearInterval(interval);
        });

        return button.progressIncrement(10);
    };

    $.fn.progressFinish = function(){
        return this.first().progressSet(100);
    };

    $.fn.progressIncrement = function(val){

        val = val || 10;

        var button = this.first();

        button.trigger('progress',[val])

        return this;
    };

    $.fn.progressSet = function(val){
        val = val || 10;

        var finish = false;
        if(val >= 100){
            finish = true;
        }

        return this.first().trigger('progress',[val, true, finish]);
    };

    // This function creates a progress meter that
    // finishes in a specified amount of time.

    $.fn.progressTimed = function(seconds, cb){

        var button = this.first(),
            bar = button.find('.tz-bar');

        if(button.is('.in-progress')){
            return this;
        }

        // Set a transition declaration for the duration of the meter.
        // CSS will do the job of animating the progress bar for us.

        bar.css('transition', seconds+'s linear');
        button.progressSet(99);

        window.setTimeout(function(){
            bar.css('transition','');
            button.progressFinish();

            if($.isFunction(cb)){
                cb();
            }

        }, seconds*1000);
    };
}(jQuery));
