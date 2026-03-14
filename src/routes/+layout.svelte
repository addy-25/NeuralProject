<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';

	import CanvasPortalTarget from '$lib/components/CanvasPortalTarget.svelte';
	import { Canvas } from '@threlte/core';
	import type { Snippet } from 'svelte';

	let { children }: { children: Snippet } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<div>
	<Canvas>
		<CanvasPortalTarget />
	</Canvas>
</div>

{@render children()}

<style>
	div {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
	}
</style>
