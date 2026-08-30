{
	"patcher" : 	{
		"fileversion" : 1,
		"appversion" : 		{
			"major" : 8,
			"minor" : 5,
			"revision" : 8,
			"architecture" : "x64",
			"modernui" : 1
		}
,
		"classnamespace" : "box",
		"rect" : [ 80.0, 95.0, 980.0, 720.0 ],
		"bglocked" : 0,
		"openinpresentation" : 1,
		"default_fontsize" : 12.0,
		"default_fontface" : 0,
		"default_fontname" : "Arial",
		"gridonopen" : 1,
		"gridsize" : [ 15.0, 15.0 ],
		"gridsnaponopen" : 1,
		"objectsnaponopen" : 1,
		"statusbarvisible" : 2,
		"toolbarvisible" : 1,
		"lefttoolbarpinned" : 0,
		"toptoolbarpinned" : 0,
		"righttoolbarpinned" : 0,
		"bottomtoolbarpinned" : 0,
		"toolbars_unpinned_last_save" : 0,
		"tallnewobj" : 0,
		"boxanimatetime" : 200,
		"enablehscroll" : 1,
		"enablevscroll" : 1,
		"devicewidth" : 0.0,
		"description" : "",
		"digest" : "",
		"tags" : "",
		"style" : "",
		"subpatcher_template" : "",
		"assistshowspatchername" : 0,
		"boxes" : [ 			{
				"box" : 				{
					"id" : "obj-plugin",
					"maxclass" : "plugin~",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 20.0, 20.0, 68.0, 20.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-plugout",
					"maxclass" : "plugout~",
					"numinlets" : 3,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 60.0, 76.0, 20.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-title",
					"maxclass" : "live.comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 140.0, 20.0, 200.0, 18.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 12.0, 8.0, 120.0, 18.0 ],
					"text" : "Context",
					"textjustification" : 0
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-health",
					"maxclass" : "live.comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 360.0, 20.0, 280.0, 18.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 140.0, 8.0, 280.0, 18.0 ],
					"text" : "sidecar health: unknown",
					"textjustification" : 0
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-host",
					"maxclass" : "live.comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 140.0, 48.0, 500.0, 18.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 12.0, 32.0, 500.0, 18.0 ],
					"text" : "host role / scope / focus",
					"textjustification" : 0
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-prompt",
					"maxclass" : "textedit",
					"numinlets" : 1,
					"numoutlets" : 4,
					"outlettype" : [ "", "int", "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 140.0, 80.0, 360.0, 28.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 12.0, 56.0, 360.0, 28.0 ],
					"text" : "add a bridge"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-run",
					"maxclass" : "live.text",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 1,
					"patching_rect" : [ 520.0, 80.0, 60.0, 28.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 380.0, 56.0, 60.0, 28.0 ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_enum" : [ "val1", "val2" ],
							"parameter_longname" : "live.text",
							"parameter_mmax" : 1,
							"parameter_shortname" : "live.text",
							"parameter_type" : 2
						}

					}
,
					"text" : "Run",
					"mode" : 0,
					"varname" : "live.text"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-dropin",
					"maxclass" : "textedit",
					"numinlets" : 1,
					"numoutlets" : 4,
					"outlettype" : [ "", "int", "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 140.0, 120.0, 360.0, 24.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 12.0, 92.0, 360.0, 24.0 ],
					"text" : "drop-in path"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-reference",
					"maxclass" : "textedit",
					"numinlets" : 1,
					"numoutlets" : 4,
					"outlettype" : [ "", "int", "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 140.0, 150.0, 360.0, 24.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 12.0, 120.0, 360.0, 24.0 ],
					"text" : "reference path"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-rev",
					"maxclass" : "live.dial",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "float" ],
					"parameter_enable" : 1,
					"patching_rect" : [ 140.0, 184.0, 48.0, 48.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 12.0, 150.0, 48.0, 48.0 ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_longname" : "Reverence",
							"parameter_mmax" : 1.0,
							"parameter_shortname" : "Rev",
							"parameter_type" : 0,
							"parameter_unitstyle" : 0
						}

					}
,
					"varname" : "live.dial"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-abs",
					"maxclass" : "live.dial",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "float" ],
					"parameter_enable" : 1,
					"patching_rect" : [ 200.0, 184.0, 48.0, 48.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 68.0, 150.0, 48.0, 48.0 ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_longname" : "Abstraction",
							"parameter_mmax" : 1.0,
							"parameter_shortname" : "Abs",
							"parameter_type" : 0,
							"parameter_unitstyle" : 0
						}

					}
,
					"varname" : "live.dial[1]"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-amount",
					"maxclass" : "live.dial",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "float" ],
					"parameter_enable" : 1,
					"patching_rect" : [ 260.0, 184.0, 48.0, 48.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 124.0, 150.0, 48.0, 48.0 ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_longname" : "Amount",
							"parameter_mmax" : 1.0,
							"parameter_shortname" : "Amt",
							"parameter_type" : 0,
							"parameter_unitstyle" : 0
						}

					}
,
					"varname" : "live.dial[2]"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-wet",
					"maxclass" : "live.dial",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "float" ],
					"parameter_enable" : 1,
					"patching_rect" : [ 320.0, 184.0, 48.0, 48.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 180.0, 150.0, 48.0, 48.0 ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_longname" : "Wet",
							"parameter_mmax" : 1.0,
							"parameter_shortname" : "Wet",
							"parameter_type" : 0,
							"parameter_unitstyle" : 0
						}

					}
,
					"varname" : "live.dial[3]"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-inspect",
					"maxclass" : "live.comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 140.0, 248.0, 500.0, 18.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 12.0, 208.0, 500.0, 18.0 ],
					"text" : "inspect: tempo / key / energy / sections / role",
					"textjustification" : 0
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-preview",
					"maxclass" : "textedit",
					"numinlets" : 1,
					"numoutlets" : 4,
					"outlettype" : [ "", "int", "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 140.0, 276.0, 500.0, 80.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 12.0, 232.0, 500.0, 80.0 ],
					"text" : "preview"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-audition",
					"maxclass" : "live.text",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 1,
					"patching_rect" : [ 140.0, 368.0, 80.0, 24.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 12.0, 320.0, 80.0, 24.0 ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_enum" : [ "val1", "val2" ],
							"parameter_longname" : "live.text[1]",
							"parameter_mmax" : 1,
							"parameter_shortname" : "live.text[1]",
							"parameter_type" : 2
						}

					}
,
					"text" : "Audition",
					"mode" : 0,
					"varname" : "live.text[1]"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-apply",
					"maxclass" : "live.text",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 1,
					"patching_rect" : [ 232.0, 368.0, 80.0, 24.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 100.0, 320.0, 80.0, 24.0 ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_enum" : [ "val1", "val2" ],
							"parameter_longname" : "live.text[2]",
							"parameter_mmax" : 1,
							"parameter_shortname" : "live.text[2]",
							"parameter_type" : 2
						}

					}
,
					"text" : "Apply",
					"mode" : 0,
					"varname" : "live.text[2]"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-status",
					"maxclass" : "live.comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 140.0, 400.0, 520.0, 18.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 12.0, 352.0, 520.0, 18.0 ],
					"text" : "If this never changes, the js object is not in THIS Live device.",
					"textjustification" : 0
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-harness",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 20.0, 260.0, 520.0, 22.0 ],
					"saved_object_attributes" : 					{
						"filename" : "/Users/camdouglas/context/max/context/code/context_harness.js",
						"parameter_enable" : 0
					}
,
					"text" : "js /Users/camdouglas/context/max/context/code/context_harness.js"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-loadbang",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"patching_rect" : [ 20.0, 230.0, 66.0, 22.0 ],
					"text" : "loadbang"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-sel-run",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "bang", "" ],
					"patching_rect" : [ 520.0, 114.0, 34.0, 22.0 ],
					"text" : "sel 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-sel-aud",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "bang", "" ],
					"patching_rect" : [ 140.0, 396.0, 34.0, 22.0 ],
					"text" : "sel 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-sel-apply",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "bang", "" ],
					"patching_rect" : [ 232.0, 396.0, 34.0, 22.0 ],
					"text" : "sel 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-msg-run",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 520.0, 140.0, 32.0, 22.0 ],
					"text" : "run"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-msg-aud",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 140.0, 422.0, 58.0, 22.0 ],
					"text" : "audition"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-msg-apply",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 232.0, 422.0, 39.0, 22.0 ],
					"text" : "apply"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-msg-snap",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 20.0, 200.0, 62.0, 22.0 ],
					"text" : "snapshot"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-bang-apply",
					"maxclass" : "button",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"patching_rect" : [ 330.0, 368.0, 24.0, 24.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 190.0, 320.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-hint",
					"maxclass" : "live.comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 140.0, 430.0, 520.0, 18.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 12.0, 376.0, 520.0, 18.0 ],
					"text" : "Press Tab for Session View. Apply writes a MIDI clip named Context.",
					"textjustification" : 0
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-prepend-set",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 20.0, 290.0, 72.0, 22.0 ],
					"text" : "prepend set"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-prepend-prompt",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 140.0, 112.0, 109.0, 22.0 ],
					"text" : "prepend setprompt"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "obj-sel-apply", 0 ],
					"source" : [ "obj-apply", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-sel-aud", 0 ],
					"source" : [ "obj-audition", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-prepend-set", 0 ],
					"source" : [ "obj-harness", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-msg-snap", 0 ],
					"source" : [ "obj-loadbang", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-harness", 0 ],
					"source" : [ "obj-msg-apply", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-msg-apply", 0 ],
					"source" : [ "obj-bang-apply", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-harness", 0 ],
					"source" : [ "obj-msg-snap", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-harness", 0 ],
					"source" : [ "obj-msg-aud", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-harness", 0 ],
					"source" : [ "obj-msg-run", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-plugout", 1 ],
					"source" : [ "obj-plugin", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-plugout", 0 ],
					"source" : [ "obj-plugin", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-harness", 0 ],
					"source" : [ "obj-prepend-prompt", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-status", 0 ],
					"source" : [ "obj-prepend-set", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-prepend-prompt", 0 ],
					"source" : [ "obj-prompt", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-sel-run", 0 ],
					"source" : [ "obj-run", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-msg-apply", 0 ],
					"source" : [ "obj-sel-apply", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-msg-aud", 0 ],
					"source" : [ "obj-sel-aud", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-msg-run", 0 ],
					"source" : [ "obj-sel-run", 0 ]
				}

			}
 ],
		"parameters" : 		{
			"obj-abs" : [ "Abstraction", "Abs", 0 ],
			"obj-amount" : [ "Amount", "Amt", 0 ],
			"obj-apply" : [ "live.text[2]", "live.text[2]", 0 ],
			"obj-audition" : [ "live.text[1]", "live.text[1]", 0 ],
			"obj-rev" : [ "Reverence", "Rev", 0 ],
			"obj-run" : [ "live.text", "live.text", 0 ],
			"obj-wet" : [ "Wet", "Wet", 0 ],
			"parameterbanks" : 			{
				"0" : 				{
					"index" : 0,
					"name" : "",
					"parameters" : [ "-", "-", "-", "-", "-", "-", "-", "-" ]
				}

			}
,
			"inherited_shortname" : 1
		}
,
		"dependency_cache" : [ 			{
				"name" : "context_harness.js",
				"bootpath" : "/Users/camdouglas/context/max/context/code",
				"patcherrelativepath" : "code",
				"type" : "TEXT",
				"implicit" : 1
			}
 ],
		"autosave" : 0
	}

}
