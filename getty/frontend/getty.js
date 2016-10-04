/**
 * the javascript file to import for semantiful differential html page
 */

var prev_hash = "";
var post_hash = "";

var isolation = false;
var iso_type = "ni";
var invdiff_display_with = "none";

var current_method_name = "";

var target_anchor_prefix = "-getty-ta-";

var load_timeout = 200;  // 0.2s

function set_commit_hashes(prev, post) {
	prev_hash = prev;
	post_hash = post;
}

function install_msg_tips(cmsg, glink) {
	config_obj = {
		position: ["154", "2"],
		persistent: true, focus: true,
		showTime: 200, hideTime: 0, hideEffect: 'none',
		onBeforeShow: function() {
			link_to_github = "";
			if (glink != "")
				link_to_github = (
					"<a href='" + glink + "' target='_blank'>" +
					"Show all commit messages and code changes at Github</a>");
			html_to_show = "<div>" + "<pre>" + cmsg + "</pre>" + link_to_github + "</div>";
			this.update(html_to_show);
		},
		onHide: function() {
			this.update("");
		}
	};
	$('a#commit-msg-link').simpletip(config_obj);
}

function fsname_to_inv_path(mtd_fsformat_name, commit_hash) {
	return "./_getty_inv__" + mtd_fsformat_name + "__" + commit_hash + "_.inv.out.html";
}

function methodInvsComparePage(theMtd, prev, post) {
	compareInvs = $("div#hide-all div#vsinvs-" + iso_type + "-" + theMtd)[0].outerHTML;
	left = 
		"width:48%;height:400px;background-color: #5A5F5A;" + 
		"display:inline-block;position:relative;border:2px dotted #A8BBA8;";
	preInvs = 
		"<iframe src='" + fsname_to_inv_path(theMtd, prev) + "' " +
				"class='invtip' style='" + left + "'></iframe>";
	right = 
		"width:48%;height:400px;background-color: #5A5F5A;" + 
		"display:inline-block;position:absolute;right:15px;border:2px dotted #A8BBA8;";
	postInvs = 
		"<iframe src='" + fsname_to_inv_path(theMtd, post) + "' " +
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
	set_commit_hashes(prev, post);
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
				};
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
				};
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
				};
				the_rows.eq(j).simpletip(config_obj);
			}
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
	return s.replace(/:/g, "_").replace(/\$/g, "_").replace(/\./g, '_');
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
	return "./_getty_allcode_" + hash_value + "_/" + rel_path + ".java.html";
}

active_lbtn_style = {"color": "blue", "background": "whitesmoke"};
inactive_lbtn_style = {"color": "gray", "background": "linear-gradient(whitesmoke, lightgray)"};

function show_src_or_inv(which) {
	if (which == "inv") {
		$('iframe.srctip').hide();
		$('iframe.srcdifftip').hide();
		tfs = fsformat(current_method_name)
		switch (iso_type) {
			case "ni":
				$('iframe#iinvprev').attr('src', fsname_to_inv_path(tfs, prev_hash));
				$('iframe#iinvpost').attr('src', fsname_to_inv_path(tfs, post_hash));
				break;
			case "si":
				$('iframe#iinvprev').attr('src', fsname_to_inv_path(tfs, prev_hash + "_" + post_hash));
				$('iframe#iinvpost').attr('src', fsname_to_inv_path(tfs, post_hash));
				break;
			case "ti4o":
				$('iframe#iinvprev').attr('src', fsname_to_inv_path(tfs, prev_hash));
				$('iframe#iinvpost').attr('src', fsname_to_inv_path(tfs, prev_hash + "_" + post_hash));
				break;
			case "ti4n":
				$('iframe#iinvprev').attr('src', fsname_to_inv_path(tfs, post_hash + "_" + prev_hash));
				$('iframe#iinvpost').attr('src', fsname_to_inv_path(tfs, post_hash));
				break;
			default:
				console.log("incorrect iso_type: " + iso_type);
		}
		$('iframe.invtip').css("display", "inline-block");
		$('a.src-inv-button-link').css(inactive_lbtn_style);
		$('a#src_inv_btn_4inv').css(active_lbtn_style);
	} else if (which == "src") {
		$('iframe.invtip').hide();
		$('iframe.srcdifftip').hide();
		anchor_name = fsformat(current_method_name);
		// reset link with anchor for better display
		$('iframe#i-left-src').attr('src', name_to_path(current_method_name, prev_hash));
		$('iframe#i-right-src').attr('src', name_to_path(current_method_name, post_hash));
		$('iframe.srctip').css("display", "inline-block");
		$('a.src-inv-button-link').css(inactive_lbtn_style);
		$('a#src_inv_btn_4src').css(active_lbtn_style);
		window.setTimeout(function() {
			$('iframe#i-left-src').ready(function() {
				$('iframe#i-left-src').attr(
						'src', name_to_path(current_method_name, prev_hash) + "#" + anchor_name);
			});
			$('iframe#i-right-src').ready(function() {
				$('iframe#i-right-src').attr(
						'src', name_to_path(current_method_name, post_hash) + "#" + anchor_name);
			});
		}, load_timeout);
	} else if (which == "srcdiff") {
		$('iframe.invtip').hide();
		$('iframe.srctip').hide();
		srcdiff_anchor_name = target_anchor_prefix + fsformat(current_method_name);
		$('iframe#i-mid-srcdiff').attr('src', './src.diff.html');
		$('iframe.srcdifftip').css("display", "inline-block");
		$('a.src-inv-button-link').css(inactive_lbtn_style);
		$('a#src_inv_btn_4srcdiff').css(active_lbtn_style);
		window.setTimeout(function() {
			$('iframe#i-mid-srcdiff').ready(function() {
				$('iframe#i-mid-srcdiff').attr('src', './src.diff.html#' + srcdiff_anchor_name);
			});
		}, load_timeout);
	} else {
		$('iframe.invtip').hide();
		$('iframe.srctip').hide();
		$('iframe.srcdifftip').hide();
		$('a.src-inv-button-link').css(inactive_lbtn_style);
		$('a#src_inv_btn_4none').css(active_lbtn_style);
	}
	invdiff_display_with = which;
	return false;
}

active_style = "color:blue;background:whitesmoke;"
inactive_style = "color:gray;background:linear-gradient(whitesmoke, lightgray);"
function create_src_or_inv_button_link(thetype, theid) {
	var theparam;
	var thetext;
	if (thetype == "inv") {
		theparam = "inv";
		thetext = "Complete Invariants";
	} else if (thetype == "src") {
		theparam = "src";
		thetext = "Source Code (No Method Diff)";
	} else if (thetype == "srcdiff") {
		theparam = "srcdiff";
		thetext = "Source Code Diff";
	} else {
		theparam = "none";
		thetext = "Invariant Diff Only";
	}
	return "<a href='#' class='src-inv-button-link' id='" + theid + "' " +
		"style=\"" + ((thetype == invdiff_display_with) ? active_style : inactive_style) + "\"" +
		"onclick='return show_src_or_inv(\"" + theparam + "\");'>" + thetext + "</a>";
}

function methodInvsCompareDiv(method_name) {
	theMtd = fsformat(method_name);
	targetInvComp = $("div#getty-full-inv-diff div#vsinvs-" + iso_type + "-" + theMtd)[0]
	
	if (targetInvComp == undefined)
		// return htmlContent = "Choose a neighbor target to show its invariant change";
		compareInvs = "<div>No invariants inferred for <b>" +
			method_name.replace(/</g, "&lt;").replace(/>/g, "&gt;") + "</b></div>";
	else
		compareInvs = targetInvComp.outerHTML;
	
	var preInvs = "", postInvs = "";
	var preSrcs = "", postSrcs = "";
	var anchor_name = fsformat(current_method_name);
	
	ileft =
		"width:49%;height:400px;background-color:#000;" +
		"display:none;position:relative;border:2px dotted #A8BBA8;";
	iright =
		"width:49%;height:400px;background-color:#000;" +
		"display:none;position:absolute;right:15px;border:2px dotted #A8BBA8;";
	sdiff =
		"width:99.2%;height:400px;display:none;padding:4px;border:2px dotted #A8BBA8;";
	preInvs =
		"<iframe id='iinvprev' name='iinvprev' src='" + fsname_to_inv_path(theMtd, prev_hash) + "' " +
		"class='invtip' style='" + ileft + "'></iframe>";
	postInvs =
		"<iframe id='iinvpost' name='iinvpost' src='" + fsname_to_inv_path(theMtd, post_hash) + "' " +
		"class='invtip' style='" + iright + "'></iframe>";
	sleft =
		"width:49%;height:400px;background-color:#333;" +
		"display:none;position:relative;border:2px dotted #A8BBA8;";
	sright =
		"width:49%;height:400px;background-color:#333;" +
		"display:none;position:absolute;right:15px;border:2px dotted #A8BBA8;";
	preSrcs =
		"<iframe id='i-left-src' src='" + name_to_path(method_name, prev_hash) + "#" + anchor_name + "' " +
		"class='srctip' style='" + sleft + "'></iframe>";
	postSrcs =
		"<iframe id='i-right-src' src='" + name_to_path(method_name, post_hash) + "#" + anchor_name + "' " +
		"class='srctip' style='" + sright + "'></iframe>";
	srcDiffs =
		"<iframe id='i-mid-srcdiff' src='" + name_to_path(method_name, post_hash) + "#" + anchor_name + "' " +
		"class='srcdifftip' style='" + sdiff + "'></iframe>";
	src_tab_choice = "";
	if (all_modified_targets.contains(method_name)) {
		if (invdiff_display_with == 'src') invdiff_display_with = 'srcdiff';
		src_tab_choice = create_src_or_inv_button_link("srcdiff", "src_inv_btn_4srcdiff");
	} else {
		if (invdiff_display_with == 'srcdiff') invdiff_display_with = 'src';
		src_tab_choice = create_src_or_inv_button_link("src", "src_inv_btn_4src");
	}
	mitabs = "<div style='margin-bottom:8px;'>" +
		"<span class='more-inv-display-option-listing menu-words'>More Display Options:</span>&nbsp;&nbsp;" +
		"<div class='link-button-tabs-bottom'>" +
		[create_src_or_inv_button_link("none", "src_inv_btn_4none"),
		 create_src_or_inv_button_link("inv", "src_inv_btn_4inv"),
		 src_tab_choice].join("&nbsp;&nbsp;") + "</div></div>";
	return compareInvs + "<br>" + mitabs + preInvs + postInvs + preSrcs + postSrcs + srcDiffs;
}

var neighborhood_table =
	"<table id='neighbors'>\n" +  
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
	display_name =
		method_name.substring(common_prefix_length)
			.replace(/</g, "&lt;").replace(/>g/, "&gt;")
			.replace(/:/g, ":&#8203;").replace(/\$/g, "&#8203;$$");
	if (all_modified_targets.contains(method_name))
		return "<u>" + display_name + "</u>";
	else
		return display_name;
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
		$("a.hidable-mtd-equal-inv").hide();
		show_methods_equal_inv = false;
	} else {
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

function output_inv_diff() {
	$('div#csi-output-invcomp').html(methodInvsCompareDiv(current_method_name));
	show_src_or_inv(invdiff_display_with);
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
	$('table#neighbors td#neighbor-center').html("<&nbsp;" + bolden_for_modified(method_name) + "&nbsp;>");
	update_neighbor(method_name, 'north', post_affected_caller_of, prev_affected_caller_of);
	update_neighbor(method_name, 'south', post_affected_callee_of, prev_affected_callee_of);
	update_neighbor(method_name, 'west', post_affected_pred_of, prev_affected_pred_of);
	update_neighbor(method_name, 'east', post_affected_succ_of, prev_affected_succ_of);
	current_method_name = method_name;
	output_inv_diff();
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

function iso_type_reset(it) {
	$('a.csi-iso-ctrl-group').css(inactive_lbtn_style);
	$('a#csi-iso-link-' + it).css(active_lbtn_style);
	iso_type = it;
	if (current_method_name != "")
		output_inv_diff();
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
