<script lang="ts">
import DataGrid from "../lib/DataGrid.svelte";
	import { _ } from 'svelte-i18n';
import DataExplorer from "../lib/DataExplorer.svelte";
import EquivalentImpacts from "../lib/EquivalentImpacts.svelte";

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
<h3 class="title-second">Ratio Scope 2 / Scope 3</h3>
<div id="stats">
	<div class="camembert-left">
		<h4>{$_('index.global-mean')}</h4>
		<canvas id="camembert" width="600" height="400"></canvas>
	</div>
</div>

<style>
    :global(:root) {
        --grid-height: 500px;
    }
</style>