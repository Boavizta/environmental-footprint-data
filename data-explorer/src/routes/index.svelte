<script lang="ts">
	import AgGrid from "@budibase/svelte-ag-grid";
	import { _ } from 'svelte-i18n';

	let data = [
		{ make: "Toyota", model: "Celica", price: 35000 },
		{ make: "Ford", model: "Mondeo", price: 32000 },
		{ make: "Porsche", model: "Boxter", price: 72000 },
	];

	let columnDefs = [
		{
			headerName: "Make",
			field: "make",
			sortable: true,
			editable: true,
		},
		{ headerName: "Model", field: "model", sortable: true },
		{ headerName: "Price", field: "price", sortable: true },
	];
</script>

<div id="navbar">
	<img id="logo" src="./boavizta-logo-4.png" alt="Boavizta">
	<h1 class="title-main">BOAVIZTA</h1>

</div>
<h1 class="title-main">{$_('index.title')}</h1>
<h3 class="title-second">Référentiel de données</h3>
<p class="text">Un des constats qui nous a incités à lancer Boavizta était que nous manquions cruellement de données
	pertinentes pour mesurer les impacts environnementaux du numérique. Au-delà des impacts liés à la consommation
	d'électricité des équipements permettant de délivrer des services numériques, il est primordial, pour mesurer
	justement, de connaitre les impacts de la fabrication, du transport et de la fin de vie de tous ces équipements.
	D'autant plus que pour certains d'entre eux, comme les terminaux et les écrans, ces phases du cycle de vie ont un
	impact bien plus important que celui lié à leur consommation électrique.</p>
<p class="text">Jusqu'à présent, les mesures d'impact de ces phases étaient complexes à mettre en oeuvre ou
	nécessitaient des données propriétaires, et impliquaient des durées et des couts bien trop importants pour être
	réalisées régulièrement, même sur des périmètres simples.</p>
<p class="text">Boavizta pense qu'une autre approche est possible et que celle-ci serait bien plus adaptée pour rendre
	accessible la mesure d'impact environnemental du numérique au plus grand nombre.</p>
<h3 class="title-second title-left">Effectuer une recherche </h3>

<AgGrid bind:data {columnDefs} />

<h3 class="title-second">Ratio Scope 2 / Scope 3</h3>
<div id="stats">
	<div class="camembert-left">
		<h4>Moyenne globale</h4>
		<canvas id="camembert" width="600" height="400"></canvas>
	</div>
</div>

<style>
    :global(:root) {
        --grid-height: 500px;
    }
</style>