/**
 * the javascript file to import for semantiful differential html page
 */

var prev_hash = "";
var post_hash = "";

//deprecated
function invstr2html(str, pos) {
	style = "width:48%;max-height:400px;overflow:auto;padding:5px 5px 5px 5px;";
	if (pos == "left")
		style += "display:inline-block;position:relative;" + 
			"border:2px dotted #A8BBA8;background:#5A5F5A;color:white;";
	else if (pos == "right")
		style += "display:inline-block;position:absolute;right:15px;" + 
			"border:2px dotted #A8BBA8;background:#5A5F5A;color:white;";
	else
		console.error('incorrect pos arg passed to invstr2html(): it should be either "left" or "right"');
	start = "<p style='" + style + "'>\n";
	body = str.replace("&", "&amp;", "g").replace("<", "&lt;", "g").replace(">", "&gt;", "g");
	body = withLineNumbers(body, 1);
	body = body.replace(/(?:\r\n|\r|\n)/g, '<br />');
	end = "\n</p>";
	return start + body + end;
}

//deprecated
function methodInvsCompare(theMtd, prev, post) {
	compareInvs = $("div#vsinvs-" + theMtd)[0].outerHTML;
	preInvs = $("invariants#" + theMtd).data(prev);
	postInvs = $("invariants#" + theMtd).data(post);
	htmlContent = compareInvs + invstr2html(preInvs, "left") + invstr2html(postInvs, "right");
	return "<body>" + htmlContent + "</body>";
}

// style for source code if needed
// style = "max-width:400px;max-height:400px;overflow:auto;padding:5px 5px 5px 5px";

//deprecated
function withLineNumbers(content, start) {
	var content_with_ln = "";
	var lines = content.split(/(?:\r\n|\r|\n)/);
	for (j = 0, i = start; j < lines.length; j ++, i ++) {
		ln = "" + i;
		if (ln.length < 3)
			ln = "&nbsp;".repeat(3 - ln.length) + ln;
		content_with_ln += ("<span>" + ln +"&nbsp;|&nbsp;&nbsp;&nbsp;</span>" + lines[j]) + "\n";
	}
	return content_with_ln;
}

//deprecated
function installInvTips_old(newl2m, oldl2m) {
	postHash = newl2m[0];
	prevHash = oldl2m[0];
	
	// add invs for newl2m
	// consider added lines
	for (i = 1; i < newl2m.length; i += 3) {
		theFile = newl2m[i];
		theLine = newl2m[i+1];
		theMethod = newl2m[i+2];
		the_rows = $("tr.diffadded." + theFile)
		for (j = 0; j < the_rows.length; j ++) {			
			if (the_rows[j].childNodes[1].innerText == theLine) {
				the_rows.eq(j).simpletip({
					fixed: true, position: 'bottom',
					onBeforeShow: function() {
						this.update(methodInvsCompare(theMethod, prevHash, postHash));
					},
					onHide: function() {
						this.update("");
					},
					showTime: 200, hideTime: 0, hideEffect: 'none'
				});
			}
		}
	}
	//consider changed lines
	for (i = 1; i < newl2m.length; i += 3) {
		theFile = newl2m[i];
		theLine = newl2m[i+1];
		theMethod = newl2m[i+2];
		the_rows = $("tr.diffchanged." + theFile)
		for (j = 0; j < the_rows.length; j ++) {			
			if (the_rows[j].childNodes[2].innerText == theLine) {
				the_rows.eq(j).simpletip({
					fixed: true, position: 'bottom',
					onBeforeShow: function() {
						this.update(methodInvsCompare(theMethod, prevHash, postHash));
					},
					onHide: function() {
						this.update("");
					},
					showTime: 200, hideTime: 0, hideEffect: 'none'
				});
			}
		}
	}
	
	// add invs for oldl2m
	// consider delted lines
	for (i = 1; i < oldl2m.length; i += 3) {
		theFile = oldl2m[i];
		theLine = oldl2m[i+1];
		theMethod = oldl2m[i+2];
		the_rows = $("tr.diffdeleted." + theFile)
		for (j = 0; j < the_rows.length; j ++) {			
			if (the_rows[j].childNodes[0].innerText == theLine) {
				the_rows.eq(j).simpletip({
					fixed: true, position: 'bottom',
					onBeforeShow: function() {
						this.update(methodInvsCompare(theMethod, prevHash, postHash));
					},
					onHide: function() {
						this.update("");
					},
					showTime: 200, hideTime: 0, hideEffect: 'none'
				});
			}
		}
	}
}

function methodInvsComparePage(theMtd, prev, post) {
	compareInvs = $("div#hide-all div#vsinvs-" + theMtd)[0].outerHTML;
	left = 
		"width:48%;height:400px;background-color: #5A5F5A;" + 
		"display:inline-block;position:relative;border:2px dotted #A8BBA8;";
	preInvs = 
		"<iframe src='./_getty_inv__" + theMtd + "__" + prev + "_.inv.html' " +
				"class='invtip' style='" + left + "'></iframe>";
	right = 
		"width:48%;height:400px;background-color: #5A5F5A;" + 
		"display:inline-block;position:absolute;right:15px;border:2px dotted #A8BBA8;";
	postInvs = 
		"<iframe src='./_getty_inv__" + theMtd + "__" + post + "_.inv.html' " +
				"class='invtip' style='" + right + "'></iframe>";
	htmlContent = compareInvs + "<br>" + preInvs + postInvs;
	return "<body>" + htmlContent + "</body>";
}

function methodName(classNames) {
	arr = classNames.split(" ");
	if (arr.length == 3)
		return arr[2].substring(9);
	else
		return undefined;
}

function installInvTips(post, prev, newl2m, oldl2m) {
	prev_hash = prev;
	post_hash = post;
	postHash = newl2m[0];
	prevHash = oldl2m[0];
	
	// add invs for newl2m
	// consider added lines
	for (i = 1; i < newl2m.length; i += 3) {
		theFile = newl2m[i];
		theLine = newl2m[i+1];
		theMethod = newl2m[i+2];
		the_rows = $("tr.diffadded." + theFile)
		for (j = 0; j < the_rows.length; j ++) {			
			if (the_rows[j].childNodes[1].innerText == theLine) {
				config_obj = {
					fixed: true, position: 'bottom', //persistent: true,
					onBeforeShow: function() {
						method_name = methodName(this.getParent().attr('class'));
						this.update(methodInvsComparePage(method_name, prevHash, postHash));
					},
					onHide: function() {
						this.update("");
					},
					showTime: 200, hideTime: 0, hideEffect: 'none'
				}
				the_rows.eq(j).simpletip(config_obj);
			}
		}
	}
	//consider changed lines
	for (i = 1; i < newl2m.length; i += 3) {
		theFile = newl2m[i];
		theLine = newl2m[i+1];
		theMethod = newl2m[i+2];
		the_rows = $("tr.diffchanged." + theFile)
		for (j = 0; j < the_rows.length; j ++) {			
			if (the_rows[j].childNodes[2].innerText == theLine) {
				config_obj = {
					fixed: true, position: 'bottom', //persistent: true,
					onBeforeShow: function() {
						method_name = methodName(this.getParent().attr('class'));
						this.update(methodInvsComparePage(method_name, prevHash, postHash));
					},
					onHide: function() {
						this.update("");
					},
					showTime: 200, hideTime: 0, hideEffect: 'none'
				}
				the_rows.eq(j).simpletip(config_obj);
			}
		}
	}
	
	// add invs for oldl2m
	// consider delted lines
	for (i = 1; i < oldl2m.length; i += 3) {
		theFile = oldl2m[i];
		theLine = oldl2m[i+1];
		theMethod = oldl2m[i+2];
		the_rows = $("tr.diffdeleted." + theFile)
		for (j = 0; j < the_rows.length; j ++) {			
			if (the_rows[j].childNodes[0].innerText == theLine) {
				config_obj = {
					fixed: true, position: 'bottom', //persistent: true,
					onBeforeShow: function() {
						method_name = methodName(this.getParent().attr('class'));
						this.update(methodInvsComparePage(method_name, prevHash, postHash));
					},
					onHide: function() {
						this.update("");
					},
					showTime: 200, hideTime: 0, hideEffect: 'none'
				}
				the_rows.eq(j).simpletip(config_obj);
			}
		}
	}
}

function installAdvisorTips(adviceFile) {
	var style = "width:1200px;height:640px;";
	$("#getty-advice-title").eq(0).simpletip({
		fixed: true, position: ["100px", "15px"],
		content: "<iframe src='./" + adviceFile + "' class='advtip' style='" + style + "'></iframe>",
		showTime: 200, hideTime: 0, hideEffect: 'none'
	})
}

function reportTipFor(theMtd, prev, post) {
	var invdiff = $("div#vsinvs-" + theMtd);
	if (invdiff.length != 1) {
		return "<span>NOT CONSIDERED</span>";
	} else {
		compareInvs = invdiff[0].outerHTML;
		left = 
			"width:48%;height:400px;background-color: #5A5F5A;" + 
			"display:inline-block;position:relative;border:2px dotted #A8BBA8;";
		preInvs = 
			"<iframe src='./_getty_inv__" + theMtd + "__" + prev + "_.inv.html' " +
					"class='invtip' style='" + left + "'></iframe>";
		right = 
			"width:48%;height:400px;background-color: #5A5F5A;" + 
			"display:inline-block;position:absolute;right:15px;border:2px dotted #A8BBA8;";
		postInvs = 
			"<iframe src='./_getty_inv__" + theMtd + "__" + post + "_.inv.html' " +
					"class='invtip' style='" + right + "'></iframe>";
		htmlContent = compareInvs + "<br>" + preInvs + postInvs;
		return "<body>" + htmlContent + "</body>";
	}
}

function installInvTips4Advice(methods, prev, post) {
	for (i = 0; i < methods.length; i ++) {
		the_spans = $(".report-" + methods[i])
		for (j = 0; j < the_spans.length; j ++) {
			this_span = the_spans.eq(j);
			config_obj = {
				fixed: true, position: 'bottom',
				onBeforeShow: function() {
					theMethod = this.getParent().attr('class').substring(7);
					this.update(reportTipFor(theMethod, prev, post));
				},
				onHide: function() {
					this.update("");
				},
				showTime: 200, hideTime: 0, hideEffect: 'none'
			}
			this_span.simpletip(config_obj);
		}
	}
}

// useful variables for CSI display
var all_project_methods; // = new buckets.Set();
var all_modified_targets; // = new buckets.Set();
var all_test_and_else; // = new buckets.Set();
var all_whose_inv_changed; // = new buckets.Set();
var post_affected_caller_of; // = new buckets.Dictionary();
var post_affected_callee_of; // = new buckets.Dictionary();
var post_affected_pred_of; // = new buckets.Dictionary();
var post_affected_succ_of; // = new buckets.Dictionary();

function real_name(s) {
	colon_index = s.lastIndexOf(":");
	if (colon_index == -1)
		return s;
	else if (s.substring(colon_index+1) == "<init>") {
		last_prd_index = s.lastIndexOf(".");
		last_dlr_index = s.lastIndexOf("$");
		chop_index = (last_prd_index > last_dlr_index ? last_prd_index : last_dlr_index);
		mtd_name = s.substring(chop_index+1, colon_index);
		return s.substring(0, colon_index+1) + mtd_name;
	} else if (s.substring(colon_index+1) == "<clinit>") {
		return s.substring(0, colon_index);
	} else {
		return s;
	}
}

function fsformat(s) {
	s = real_name(s);
	return s.replace(":", "_", "g").replace("$", "_", "g").replace(/\./g, '_');
}

function methodInvsCompareDiv(method_name) {
	theMtd = fsformat(method_name);
	compareInvs = $("div#hide-all div#vsinvs-" + theMtd)[0].outerHTML;
	left = 
		"width:49%;height:400px;background-color: #5A5F5A;" + 
		"display:inline-block;position:relative;border:2px dotted #A8BBA8;";
	preInvs = 
		"<iframe src='./_getty_inv__" + theMtd + "__" + prev_hash + "_.inv.html' " +
		"class='invtip' style='" + left + "'></iframe>";
	right = 
		"width:49%;height:400px;background-color: #5A5F5A;" + 
		"display:inline-block;position:absolute;right:15px;border:2px dotted #A8BBA8;";
	postInvs = 
		"<iframe src='./_getty_inv__" + theMtd + "__" + post_hash + "_.inv.html' " +
		"class='invtip' style='" + right + "'></iframe>";
	return htmlContent = compareInvs + "<br>" + preInvs + postInvs;
}

var neighborhood_table =
	"<style>\n" + 
	"  td.exist-neighbor { border:dotted; padding:10px; text-align:center; }\n" + 
	"  table#neighbors a { display:inline-block; }\n" + 
	"  table#neighbors span { display:inline-block; }\n</style>" +
	"<table id='neighbors' style='table-layout:fixed;'>\n" +  
	"<tr><td></td><td id='neighbor-north' class='exist-neighbor'>north</td><td></td><tr>\n" +
	"<tr><td id='neighbor-west' class='exist-neighbor'>west</td>\n" + 
	"<td id='neighbor-center' class='exist-neighbor'>center</td>" + 
	"<td id='neighbor-east' class='exist-neighbor'>east</td><tr>\n" +
	"<tr><td></td><td id='neighbor-south' class='exist-neighbor'>south</td><td></td><tr>\n" +
	"</table>\n";

function bolden_for_modified(method_name) {
	if (all_modified_targets.contains(method_name))
		return "<b>" + method_name + "</b>";
	else
		return method_name;
}

function active_link_for(method_name, count) {
	js_cmd = "return structure_neighbors(\"" + method_name + "\");";
	return "<a href='#' onclick='" + js_cmd + "'>" + bolden_for_modified(method_name) + " (" + count + ")" + "</a>";
}

function span_for_test_else(method_name, count) {
	return "<span>" + bolden_for_modified(method_name) + " (" + count + ")" + "</a>";
}

function update_neighbor(method_name, direction, ref_var) {	
	html_content = ""
	map_result = ref_var.get(method_name);
	if (map_result == undefined)
		html_content = "none";
	else {
		all_link_elements = [];
		all_keys = map_result.keys();
		for (i = 0; i < all_keys.length; i ++) {
			affected_method = all_keys[i];
			if (all_project_methods.contains(affected_method) && 
					all_whose_inv_changed.contains(affected_method) && 
					!all_test_and_else.contains(affected_method)) {				
				affected_count = map_result.get(affected_method);
				all_link_elements.push(active_link_for(affected_method, affected_count));
			} else if (all_test_and_else.contains(affected_method)) {
				affected_count = map_result.get(affected_method);
				all_link_elements.push(span_for_test_else(affected_method, affected_count));
			}
		}
		html_content = all_link_elements.join("&nbsp;,&nbsp;");
	}
	$('table#neighbors td#neighbor-' + direction).html(html_content);
}

function output_inv_diff(method_name) {
	$('div#csi-output-invcomp').html(methodInvsCompareDiv(method_name));
}

function structure_neighbors(method_name) {
	$('div#csi-output-neighbors').html(neighborhood_table);
	$('table#neighbors td#neighbor-center').html("&lt;&nbsp;" + bolden_for_modified(method_name) + "&nbsp;&gt;");
	update_neighbor(method_name, 'north', post_affected_caller_of);
	update_neighbor(method_name, 'south', post_affected_callee_of);
	update_neighbor(method_name, 'west', post_affected_pred_of);
	update_neighbor(method_name, 'east', post_affected_succ_of);
	output_inv_diff(method_name);
	return false;
}

function activateNeighbors(method_name) {
	$('a.target-linkstyle').css("border", "none");
	$("a#target-link-" + fsformat(method_name)).css("border", "dashed");
	structure_neighbors(method_name);
	output_inv_diff(method_name);
	return false;
}

function list_to_set(lst) {
	var temp = new buckets.Set();
	for (i = 0; i < lst.length; i ++) {
		temp.add(lst[i]);
	}
	return temp;
}

function list_list_to_dict_dict(lst_lst) {	
	var temp = new buckets.Dictionary();
	for (i = 0; i < lst_lst.length - 1; i += 2) {
		the_key = lst_lst[i];
		serialized_map = lst_lst[i+1];
		tm = new buckets.Dictionary();
		for (j = 0; j < serialized_map.length - 1; j += 2) {
			tm.set(serialized_map[j], serialized_map[j+1]);
		}
		temp.set(the_key, tm);
	}
	return temp;
}
