extends SceneTree


const VisualProofScene = preload(
	"res://scenes/runtime_comparison/python_sidecar_visual_proof.tscn"
)


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	var visual = VisualProofScene.instantiate()
	root.add_child(visual)
	await process_frame
	var result: Dictionary = await visual.run_f8_cancellation_test(_hold_msec())
	printerr("Process-death test runtime was not externally terminated: %s" % JSON.stringify(result))
	quit(2)


func _hold_msec() -> int:
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--hold-msec="):
			return maxi(1_000, int(argument.trim_prefix("--hold-msec=")))
	return 30_000
