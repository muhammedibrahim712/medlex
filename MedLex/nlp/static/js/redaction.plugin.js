// var tagList = ['Name', 'Tattoos', 'Scar', 'Piercing', 'Date of Birth', 'Job'];
// var sentenceList = [
// 'Vasiliy is an architect, multi-platform developer, hobbyist UI designer, and entrepreneur.',
// 'He\'s an all-in-one performer and perfectionist in a great way. With more than sixteen years of experience in web programming and managing development teams, he\'s excited about the way the web is evolving and likes to be on the bleeding edge of modern technology.'
// ];
// var formattedSentenceList = [];
// var redactionList = [{
// 	str: "UI designer",
// 	tagId: 5
// }];
//
// var redactionSentenceMap = {
// 	"0": [0]
// };

var EventHandler = function () {

	var onClickTagComboBox = function () {
		$(".item-tagComboBox").click(function() {
			var self = $(this);
			var appendBox = $('.item-tagComboBox-append-box');

			if(appendBox.hasClass('m--hide') == true) {
				appendBox.removeClass('m--hide');
				self.find('i').removeClass('la-angle-down').addClass('la-angle-up');
				$(".not-append-box").addClass('m--hide');
			} else {
				appendBox.addClass('m--hide');
				self.find('i').removeClass('la-angle-up').addClass('la-angle-down');
				$(".not-append-box").removeClass('m--hide');
			}
		});
	}

	var onClickCreateTagButton = function() {
		$('.createNew-button button').click(function() {
			$(".createNew-detail").removeClass('m--hide');
			$(this).parent().addClass('m--hide');
		});
	}

	var onClickConfirmCreateTagButton = function() {
		$('#btn_confirmCreateTag').click(function() {
			var tagName = $('#input_newTagName').val().trim();
			if(tagName != '') {
				if(inTagList(tagName) == false) {
					$.post('addTag', {
						tagName: tagName
					}, function(data) {
						if(data.type == 'success') {
							tagId = tagList.length;
							tagList[tagId] = tagName;
							InitContextMenuTagList.appendTagNameToList(tagId, tagName);
						}
					});

				}
			}
		});

		function inTagList(tagName) {
			var lowwerCaseTagName = tagName.toLowerCase();
			for(var i = 0; i < tagList.length; i++) {
				if(tagList[i].toLowerCase() == lowwerCaseTagName)
					return true;
			}
			return false;
		}
	}

	var onClickCancelCreateTagButton = function() {
		$('#btn_cancelCreateTag').click(function() {
			$('.createNew-button').removeClass('m--hide');
			$('.createNew-detail').addClass('m--hide');
		});
	}

	var onClickRedaction = function() {
		$(document).on('click', '*[class^="redaction-"]', function() {
			var self = $(this);
			var position = $(this).offset();
			console.log(position);
			var className = $(this).attr('class');

			var tmpArr = className.split('-');
			$('.drop-down-menu').attr('redaction', tmpArr[1] + '-' + tmpArr[2] + '-' + tmpArr[3]);
			$('.item-tagComboBox').children().first().text(tagList[tmpArr[2]]);

			$('.drop-down-menu').css('left', position.left - 2 + 'px');
			$('.drop-down-menu').css('top', position.top + 26 +'px');
			$('.drop-down-menu').hide();
			$('.drop-down-menu').removeClass('m--hide');
			$('.drop-down-menu').slideDown();
		});
	}

	var onClickItemOption = function() {
		$(document).on('click', ".item-tagComboBox-append-list-option", function() {
			var self = $(this);
			
			var redactionAttr = self.parents('.drop-down-menu').attr('redaction');
			var tmpArr = redactionAttr.split('-');
			var redactionId = tmpArr[0];
			var newTagId = self.attr('tag-id');
			var oldTagId = redactionList[redactionId]['tagId'];

			if(newTagId != oldTagId) {
				$.post('changeRedactionTag', {
					redactionId: redactionList[redactionId]['id'],
					tagNameNew: tagList[newTagId],
				}, function(data) {
					if(data.type == 'success') {
						redactionList[redactionId]['tagId'] = newTagId;

						$('.drop-down-menu').attr('redaction', tmpArr[0] + '-' + newTagId + '-' + tmpArr[2]);
						$('.item-tagComboBox').children().first().text(tagList[newTagId]);

						//Convert redaction class
						var oldRedactionClassName = 'redaction-' + tmpArr[0] + '-' + oldTagId + '-' + tmpArr[2];
						var newRedactionClassName = 'redaction-' + tmpArr[0] + '-' + newTagId + '-' + tmpArr[2];
						$('.' + oldRedactionClassName).each(function() {
							$(this).attr('class', newRedactionClassName);
						});
					}
				});

			}

			$(".drop-down-menu").hide();
		});
	}

	var onBody = function() {
		$("body").click(function(e) {
			var target = e.target;
			if(target['className'].includes('redaction') == true) {
				return;
			}

		    if(target.closest('.drop-down-menu') == null) {
		    	$('.drop-down-menu').hide();
		    }
		});
	}

	var removeRedaction = function(redactionId, tagId, sentenceId) {
        $.post('removeRedactionById', {
			redactionId: redactionList[redactionId]['id']
		}, function(data) {
			if(data.type == 'success') {
				var redactionClassName = 'redaction-' + redactionId + '-' + tagId + '-' + sentenceId;
				var target = $("span." + redactionClassName);
				target.replaceWith(target.html());

				var sentenceIdList = redactionSentenceMap[redactionId+''];
				if(sentenceIdList != undefined) {
					sentenceIdList = sentenceIdList.filter(function (item) {
						return item != sentenceId;
					})
				}
				checkRedactionRemain();
			}
		});
	}

	var removeAllRedactions = function() {
		redactionList.forEach(function(redactionInfo, redactionId) {
			var tagId = redactionInfo['tagId'];
			var sentenceIdList = redactionSentenceMap[redactionId+''];
			if(sentenceIdList != undefined) {
                sentenceIdList.forEach(function (sentenceId) {
                    removeRedaction(redactionId, tagId, sentenceId);
                })
            }
		})
	}

	var acceptRedaction = function(redactionId) {
		$.post('acceptRedactionById', {
			redactionId: redactionList[redactionId]['id']
		}, function(data) {
			if(data.type == 'success') {
				redactionList[redactionId]['state'] = 1;
				$('*[class^="redaction-'+redactionId+'"]').attr('class', '').addClass('redaction_accepted');
				checkRedactionRemain();
			}
		});
	}

	var acceptAllRedaction = function() {
		$.post('acceptAllRedaction', {
			page: page
		}, function(data) {
			if(data.type == 'success') {
				for(var i = 0; i < redactionList.length; i++) {
					redactionList[i]['state'] = 1;
				}
				$('*[class^="redaction-"]').attr('class', '').addClass('redaction_accepted');
				checkRedactionRemain();
			}
		});

	}

	var onAcceptButton = function() {
		$("#div_acceptButton").click(function() {
			var redaction = $(this).parents('.drop-down-menu').attr('redaction');
			var tmpArr = redaction.split('-');
			acceptRedaction(tmpArr[0]);
			// removeRedaction(tmpArr[0], tmpArr[1], tmpArr[2]);
			$('.drop-down-menu').hide();

		});
	}

	var onAcceptAllButton = function() {
		$("#div_acceptAllButton").click(function() {
			acceptAllRedaction();
			$('.drop-down-menu').hide();
		});
	}

	var onEditButton = function() {
		$("#div_editButton").click(function() {
			var redaction = $(this).parents('.drop-down-menu').attr('redaction');
			var tmpArr = redaction.split('-');	//redactionId-tagId-sentenceId
			var sentence = sentenceList[tmpArr[2]];
			
			$('.drop-down-menu').hide();
			$("#p_editContent").html(sentence);
			$("#modal_edit").modal('show');
		});
	}

	var onSaveChangesEditBox = function() {
		$("#modal_edit #button_saveChange").click(function() {
			var newRedactionStr = "";
		    if (window.getSelection) {
		        newRedactionStr = window.getSelection().toString();
		    } else if (document.selection && document.selection.type != "Control") {
		        newRedactionStr = document.selection.createRange().text;
		    }

		    var redaction = $('.drop-down-menu').attr('redaction');
			var tmpArr = redaction.split('-');	//redactionId-tagId-sentenceId
			redactionList[tmpArr[0]]['str'] = newRedactionStr;
			$.post('changeRedactionStr', {
				str: newRedactionStr,
				id: redactionList[tmpArr[0]]['id']
			}, function(data) {
				if(data.type == 'success') {
					$("#modal_edit #button_closeModal").click();
					DisplayPage.init();
				}
			});

		});
	}

	var onRemoveButton = function() {
		$("#div_removeButton").click(function() {
			var redaction = $(this).parents('.drop-down-menu').attr('redaction');
			var tmpArr = redaction.split('-');

			removeRedaction(tmpArr[0], tmpArr[1], tmpArr[2]);
			$('.drop-down-menu').hide();
		});
	}

	var onShowReport = function() {
		$("#btn_showreport").click(function() {
			var self = this;
			$.post('getRedactionInfoForReport', function(data) {
				var tagArray = JSON.parse(data.tag_list_json);
				var redactionArray = JSON.parse(data.redaction_list_json);

				var tagMap = {};
				for(var i = 0; i < tagArray.length; i++) {
					tagMap[tagArray[i]['pk'] + ''] = tagArray[i]['fields']['name'];
				}

				var tmpMap = {};
				$(".tr-append").each(function( index ) {
				  var self = this;
				  $(self).empty();
				  $(self).remove();
				});

				for(var i = 0; i < redactionArray.length; i++) {
					var trAppendStr = 	"<tr class = 'tr-append'>" +
											"<td align = 'center'>"+(parseInt(redactionArray[i]['fields']['page'])+1) +"</td>" +
											"<td>"+redactionArray[i]['fields']['str'] +"</td>" +
											"<td align = 'center'>"+tagMap[redactionArray[i]['fields']['tag']+''] +"</td>" +
										"</tr>";
					$(".tr-last").before(trAppendStr);
				}
			});
			if($(self).hasClass('show')) {
				$(self).removeClass('show').addClass('hide');
				$(self).text('HIDE REPORT');
				$("#div_report").removeClass('m--hide');
				$(".none-report").addClass('m--hide');
			} else {
				$(self).removeClass('hide').addClass('show');
				$(self).text('SHOW REPORT');
				$("#div_report").addClass('m--hide');
				$(".none-report").removeClass('m--hide');
			}
		});

	}

	var onAcceptAllButtonRightPanel = function() {
		$("#btn_acceptAllRedaction").click(function() {
			acceptAllRedaction();
			$('.drop-down-menu').hide();
		});
	}

	var onAddRedactions = function() {
		$("#btn_confirmCustomRedaction").click(function() {
			var self = this;
			var redaction = {}
			redaction['str'] = $("#input_customRedaction").val();
			if(redaction['str'] == '') {
				return;
			}
			redaction['tagName'] = tagList[$("#select_redaction").val()];
			redaction['page'] = page;
			redaction['state'] = 0;
			$.post('addRedaction', {
				str: redaction['str'],
				tagName: redaction['tagName'],
				page: redaction['page'],
			}, function(data) {
				if(data.type == 'success') {
					getSentenceList();
				}
			});
		});
	}

	var onAddCustomSelection = function() {
		$("#btn_addCustomRedaction").click(function() {
			InitTagOptions();
			$("#div_addCustomRedaction").removeClass('m--hide');
		});

		function InitTagOptions() {
			$("#select_redaction").empty();
			tagList.forEach(function(tagName, tagId) {
				$("#select_redaction").append('<option value = "'+ tagId +'">' + tagName + '</option>');
			});
		}
	}

	var onConfirmAddCustomRedaction = function() {
        $('#btn_confirmCustomRedaction').click(function () {
            var newRedaction = $("#input_customRedaction").val();
            var tagId = $("#select_redaction").val();
            var newRedactionId = redactionList.length;
            if (isExistRedaction(newRedaction) == false) {
                redactionList[newRedactionId] = {};
                redactionList[newRedactionId]['str'] = newRedaction;
                redactionList[newRedactionId]['tagId'] = tagId;
                redactionSentenceMap[newRedactionId + ''] = [];

                // var lowerCaseRedactionStr = newRedaction.toLowerCase();
                sentenceList.forEach(function (sentence, sentenceId) {
                    if (sentence.includes(newRedaction) == true) {
                        redactionSentenceMap[newRedactionId + ''].push(sentenceId);
                    }
                });

                DisplayPage.init();
            }

            function isExistRedaction(redaction) {
                var lowwerCaseRedaction = redaction.toLowerCase();
                for (var i = 0; i < redactionList.length; i++) {
                    if (redactionList[i]['str'].toLowerCase() == lowwerCaseRedaction)
                        return true;
                }
                return false;
            }
        });
    };



	return {
		init: function() {
			onClickTagComboBox();
			onClickCreateTagButton();
			onClickConfirmCreateTagButton();
			onClickCancelCreateTagButton();
			onClickRedaction();
			onClickItemOption();
			onBody();

			onEditButton();
			onSaveChangesEditBox();
			onAcceptButton();
			onAcceptAllButton();
			onRemoveButton();

			onShowReport();
			onAcceptAllButtonRightPanel();
			onAddRedactions();
			onAddCustomSelection();	
			onConfirmAddCustomRedaction();
		}
	};
}();

var DisplayPage = function() {

	var formatSentence = function(redactionInfo, redactionId) {

		var sentenceIdList = redactionSentenceMap[redactionId+''];
		var str = redactionInfo['str'];
		var classStr = (redactionInfo['state']==1)?('redaction_accepted'):'';
		sentenceIdList.forEach(function(sentenceId) {
			var tmp = new RegExp(str, 'g');
			if(classStr == '')
				classStr = 'redaction-' + redactionId + '-' + redactionInfo.tagId +  '-' + sentenceId;
			formattedSentenceList[sentenceId] = formattedSentenceList[sentenceId].replace(tmp, '<span class = "'+classStr+'">' + str + '</span>');
			if(tagList[redactionInfo['tagId']] == 'Phone numbers') {
				formattedSentenceList[sentenceId] = formattedSentenceList[sentenceId].replace(str, '<span class = "'+classStr+'">' + redactionInfo['str'] + '</span>');
			}
		});
	};

	var formatPage = function() {
		formattedSentenceList = JSON.parse(JSON.stringify(sentenceList));
		redactionList.forEach(function(redactionInfo, index) {
			formatSentence(redactionInfo, index);
		})
	};

	var displaySentences = function() {

		var content = "";
		formattedSentenceList.forEach(function(sentence, index) {
			content += sentence + ' ';
		});

		$("#p_pageContent").html(content);
	};

	var calcInitRedactionCount = function() {
		var cnt = 0;
		var searchRegExpStr = '';
		redactionList.forEach(function(redaction) {
			searchRegExpStr += redaction.str + '|';
		});
		searchRegExpStr = searchRegExpStr.slice(0, -1);

		var searchRegExp = new RegExp(searchRegExpStr, "g");
		sentenceList.forEach(function(sentence) {
			cnt += (sentence.match(searchRegExp) || []).length;
		});

		redactionRemainCount = cnt;
		$("#div_redactionRemainCount").text(redactionRemainCount + ' redactions envisaged');
	};

	return {
		init: function() {
			formatPage();
			displaySentences();
			calcInitRedactionCount();
			checkRedactionRemain();
		}
	}
}();

var InitContextMenuTagList = function() {

	var initFunction = function() {
		var appendStr = '';
		tagList.forEach(function(tagName, tagId) {
			appendTagList(tagId, tagName);
		});
	}

	var appendTagList = function(tagId, tagName) {
		var appendStr = "<div class = 'item item-tagComboBox-append-list-option' tag-id = '" + tagId + "'>" + tagName + "</div>";
		$(".item.item-tagComboBox-append-list").append(appendStr);
	}

	return {
		init: function() {
			initFunction();
		},
		appendTagNameToList: function(tagId, tagName) {
			appendTagList(tagId, tagName);
		}
	}
}();

var RedactionPlugin = function() {
	return {
		init: function() {
			EventHandler.init();
			DisplayPage.init();
			InitContextMenuTagList.init();
		}
	}
}();

$(function(){
	// RedactionPlugin.init();
});
