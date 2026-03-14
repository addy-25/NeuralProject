<script lang="ts">
	import {
		addCanvasPortalSnippet,
		removeCanvasPortalSnippet
	} from '$lib/components/CanvasPortalTarget.svelte';
	import { onDestroy, type Snippet } from 'svelte';

	let { children }: { children: Snippet } = $props();

	const snippet: Snippet = () => children();
	addCanvasPortalSnippet(snippet);

	onDestroy(() => {
		removeCanvasPortalSnippet(snippet);
	});
</script>
