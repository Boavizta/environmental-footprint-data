<script lang="ts">

		import { _ } from 'svelte-i18n';
	import DataExplorer from "../lib/DataExplorer.svelte";

</script>

<div id="navbar">
	<img id="logo" src="./boavizta-logo-4.png" alt="Boavizta">
	<h1 class="title-main">BOAVIZTA</h1>

</div>
<h1 class="title-main">{$_('index.title')}</h1>
<h3 class="title-second">{$_('index.sub-title')}</h3>
<p class="text">{$_('index.statement')}</p>
<p class="text">{$_('index.impact-measure')}</p>
<p class="text">{$_('index.approach')}</p>
<h3 class="title-second title-left">{$_('index.search')}</h3>

<DataExplorer />

<style>
    :global(:root) {
        --grid-height: 500px;
    }
</style>