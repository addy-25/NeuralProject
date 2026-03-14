<script lang="ts">
	import CanvasPortal from '$lib/components/CanvasPortal.svelte';
	import CanvasSceneContent from '$lib/components/CanvasSceneContent.svelte';
</script>

<!-- Regular DOM elements for UI -->
<button>Click me</button>
<!-- 3D content -->
<CanvasPortal>
	<CanvasSceneContent />
</CanvasPortal>
