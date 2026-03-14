<script lang="ts">
	import { addCanvasPortalSnippet, removeCanvasPortalSnippet } from '$lib/components/Target.svelte';
	import { onMount, type Snippet } from 'svelte';

	let { children }: { children: Snippet } = $props();

	onMount(() => {
		addCanvasPortalSnippet(children);

		return () => {
			removeCanvasPortalSnippet(children);
		};
	});
</script>
