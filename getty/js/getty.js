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
						fixed: true, position: 'bottom', persistent: true,
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
						fixed: true, position: 'bottom', persistent: true,
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
						fixed: true, position: 'bottom', persistent: true,
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
var all_project_methods;  // = new buckets.Set();
var all_modified_targets;  // = new buckets.Set();
var all_changed_tests;  // = new buckets.Set();
var old_changed_tests;  // = new buckets.Set();
var new_changed_tests;  // = new buckets.Set();
var all_test_and_else;  // = new buckets.Set();
var all_whose_inv_changed;  // = new buckets.Set();
var all_whose_clsobj_inv_changed;  // = new buckets.Set();
var prev_affected_caller_of;  // = new buckets.Dictionary();
var prev_affected_callee_of;  // = new buckets.Dictionary();
var prev_affected_pred_of;  // = new buckets.Dictionary();
var prev_affected_succ_of;  // = new buckets.Dictionary();
var post_affected_caller_of;  // = new buckets.Dictionary();
var post_affected_callee_of;  // = new buckets.Dictionary();
var post_affected_pred_of;  // = new buckets.Dictionary();
var post_affected_succ_of;  // = new buckets.Dictionary();

var show_source_code = false;
var show_full_invariant = false;

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

function name_to_path(m, hash_value) {
	colon_index = m.lastIndexOf(":");
	dollar_index = m.indexOf("$");
	var rel_path;
	if (colon_index != -1) {  // this is a method
		if (dollar_index == -1) {  // not an inner one
			rel_path = m.substring(0, colon_index).replace(/\./g, "/");
		} else {  // an inner one
			rel_path = m.substring(0, dollar_index).replace(/\./g, "/");
		}
	} else {  // this is a class
		if (dollar_index == -1) {  // not an inner one
			rel_path = m.replace(/\./g, "/");
		} else {  // an inner one
			rel_path = m.substring(0, dollar_index).replace(/\./g, "/");
		}
	}
	return "./_getty_allcode_" + hash_value + "_/" + rel_path + ".java";
}

function methodInvsCompareDiv(method_name) {
	theMtd = fsformat(method_name);
	targetInvComp = $("div#hide-all div#vsinvs-" + theMtd)[0]
	if (targetInvComp == undefined)
		// return htmlContent = "Choose a neighbor target to show its invariant change";
		compareInvs = "<div>No Invariant Differences</div>";
	else
		compareInvs = targetInvComp.outerHTML;
	if (show_source_code || show_full_invariant) {		
		left = 
			"width:49%;height:400px;background-color: #5A5F5A;" + 
			"display:inline-block;position:relative;border:2px dotted #A8BBA8;";
		right = 
			"width:49%;height:400px;background-color: #5A5F5A;" + 
			"display:inline-block;position:absolute;right:15px;border:2px dotted #A8BBA8;";
		var preInvs = "", postInvs = "";
		var preSrcs = "", postSrcs = "";
		if (show_full_invariant) {
			// legacy - used to show invariants 
			preInvs =
				"<iframe src='./_getty_inv__" + theMtd + "__" + prev_hash + "_.inv.html' " +
				"class='invtip' style='" + left + "'></iframe>";
			// legacy - used to show invariants
			postInvs =
				"<iframe src='./_getty_inv__" + theMtd + "__" + post_hash + "_.inv.html' " +
				"class='invtip' style='" + right + "'></iframe>";
		}
		if (show_source_code) {
			console.log(method_name);
			preSrcs = "<br>" +
				"<iframe src='" + name_to_path(method_name, prev_hash) + "' " +
				"class='srctip' style='" + left + "'></iframe>";
			postSrcs =
				"<iframe src='" + name_to_path(method_name, post_hash) + "' " +
				"class='srctip' style='" + right + "'></iframe>";
		}
		return htmlContent = compareInvs + "<br>" + preInvs + postInvs + preSrcs + postSrcs;
	} else {		
		return htmlContent = compareInvs + "<br>";
	}
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

// common_package discovered and set by getty
// it exists only if 
//		(1) there is only one non-zero length common prefix, and 
//		(2) it is long enough with at least one period
var common_package = '';
var common_prefix_length = 0;

function bolden_for_modified(method_name) {
	if (all_modified_targets.contains(method_name))
		return "<b><u>" + method_name.substring(common_prefix_length) + "</u></b>";
	else
		return method_name.substring(common_prefix_length);
}

function relative_count_format(map_post, map_prev, affected_method) {
	new_count = map_post.get(affected_method);
	if (new_count == undefined)
		return "0";
	else {
		if (map_prev == undefined)
			return "0+" + new_count;
		old_count = map_prev.get(affected_method);
		if (old_count == undefined)
			return "0+" + new_count;
		else {
			new_count_int = parseInt(new_count);
			old_count_int = parseInt(old_count);
			count_diff = new_count_int - old_count_int;
			if (count_diff >= 0)
				return old_count + "+" + count_diff;
			else
				return old_count + count_diff;
		}
	}
}

var show_methods_equal_inv = true;
var show_test_methods_neighbor = true;

function toggle_show_invequal() {
	if (show_methods_equal_inv) {
		$("div#csi-output-menu a#whether-show-invequal").text("Showing More Methods: NO");
		$("a.hidable-mtd-equal-inv").hide();
		show_methods_equal_inv = false;
	} else {
		$("div#csi-output-menu a#whether-show-invequal").text("Showing More Methods: YES");
		$("a.hidable-mtd-equal-inv").show();
		show_methods_equal_inv = true;
	}
	return false;
}

function toggle_show_tests() {
	if (show_test_methods_neighbor) {
		$("div#csi-output-menu a#whether-show-tests").text("Showing Tests: NO");
		$("a.hidable-test-mtd-neighbor").hide();
		show_test_methods_neighbor = false;
	} else {
		$("div#csi-output-menu a#whether-show-tests").text("Showing Tests: YES");
		$("a.hidable-test-mtd-neighbor").show();
		show_test_methods_neighbor = true;
	}
	return false;
}

function active_link_for(method_name, count) {
	js_cmd = "return structure_neighbors(\"" + method_name + "\");";
	return "<a href='#' class='special-neighbor-link' onclick='" + js_cmd + "'>" + bolden_for_modified(method_name) + " (" + count + ")" + "</a>";
}

function active_hidable_link_for(method_name, count) {
	js_cmd = "return structure_neighbors(\"" + method_name + "\");";
	return "<a href='#' class='hidable-mtd-equal-inv' onclick='" + js_cmd + "'>" + bolden_for_modified(method_name) + " (" + count + ")" + "</a>";
}

function active_hidable_test_link_for(method_name, count) {
	js_cmd = "return structure_neighbors(\"" + method_name + "\");";
	return "<a href='#' class='hidable-test-mtd-neighbor special-neighbor-link' onclick='" + js_cmd + "'>" + bolden_for_modified(method_name) + " (" + count + ")" + "</a>";
}

function span_for_test(method_name, count) {
	// legacy code use span, but now we prefer to use links
//	return "<span class='hidable-test-mtd-neighbor hidable-mtd-equal-inv'><b>" + bolden_for_modified(method_name) + " (" + count + ")" + "</b></span>";
	js_cmd = "return structure_neighbors(\"" + method_name + "\");";
	return "<a href='#' class='hidable-test-mtd-neighbor hidable-mtd-equal-inv' onclick='" + js_cmd + "'>" + bolden_for_modified(method_name) + " (" + count + ")" + "</a>";
}

function update_neighbor(method_name, direction, ref_var, ref_prev_var) {	
	html_content = ""
	map_result = ref_var.get(method_name);
	var map_prev_result;
	if (ref_prev_var == undefined)
		map_prev_result = undefined;
	else
		map_prev_result = ref_prev_var.get(method_name);
	if (map_result == undefined)
		html_content = "none";
	else {
		all_link_elements = [];
		all_link_tests = [];
		all_keys = map_result.keys();
		for (i = 0; i < all_keys.length; i ++) {
			affected_method = all_keys[i];
			if (all_project_methods.contains(affected_method) 
					&& !all_test_and_else.contains(affected_method)) {
				affected_count = relative_count_format(map_result, map_prev_result, affected_method);
				if (all_whose_inv_changed.contains(affected_method)) {
					all_link_elements.unshift(active_link_for(affected_method, affected_count));
				} else {
					all_link_elements.push(active_hidable_link_for(affected_method, affected_count));
				}
			} else if (all_changed_tests.contains(affected_method)) {
				affected_count = relative_count_format(map_result, map_prev_result, affected_method);
				if (all_whose_inv_changed.contains(affected_method)) {
					all_link_tests.unshift(active_hidable_test_link_for(affected_method, affected_count));
				} else {					
					all_link_tests.push(span_for_test(affected_method, affected_count));
				}
			}
		}
		all_link_elements = all_link_elements.concat(all_link_tests);
//		html_content = all_link_elements.join("<br>");
		html_content = all_link_elements.join("&nbsp;&nbsp;");
	}
	$('table#neighbors td#neighbor-' + direction).html(html_content);
}

function output_inv_diff(method_name) {
	$('div#csi-output-invcomp').html(methodInvsCompareDiv(method_name));
}

function selected_show_hide() {
	if (show_methods_equal_inv) {
		$("a.hidable-mtd-equal-inv").show();
	} else {
		$("a.hidable-mtd-equal-inv").hide();
	}
	if (show_test_methods_neighbor) {
		$("a.hidable-test-mtd-neighbor").show();
	} else {
		$("a.hidable-test-mtd-neighbor").hide();
	}
}

function structure_neighbors(method_name) {
	$('div#csi-output-neighbors').html(neighborhood_table);
	$('table#neighbors td#neighbor-center').html("&lt;&nbsp;" + bolden_for_modified(method_name) + "&nbsp;&gt;");
	update_neighbor(method_name, 'north', post_affected_caller_of, prev_affected_caller_of);
	update_neighbor(method_name, 'south', post_affected_callee_of, prev_affected_callee_of);
	update_neighbor(method_name, 'west', post_affected_pred_of, prev_affected_pred_of);
	update_neighbor(method_name, 'east', post_affected_succ_of, prev_affected_succ_of);
	output_inv_diff(method_name);
	selected_show_hide();
	return false;
}

function activateNeighbors(method_name) {
	$('a.target-linkstyle').css("border", "none");
	$("a.class-target-link-" + fsformat(method_name)).css("border", "solid green");
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
