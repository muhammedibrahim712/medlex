    function htmlbodyHeightUpdate(){
		var height3 = window.innerHeight
						|| document.documentElement.clientHeight
						|| document.body.clientHeight;
		var height1 = $('.nav').height()
		height2 = $('.main').height()
		if(height2 > height3){
			$('html').height(Math.max(height1,height3,height2));
			$('body').height(Math.max(height1,height3,height2));
		}
		else
		{
			$('html').height(Math.max(height1,height3,height2));
			$('body').height(Math.max(height1,height3,height2));
		}
		
	}
	$(document).ready(function () {
		htmlbodyHeightUpdate()
		$( window ).resize(function() {
			htmlbodyHeightUpdate()
		});
		$( window ).scroll(function() {
			// height2 = $('.main').height()
  			// htmlbodyHeightUpdate()
		});
	});