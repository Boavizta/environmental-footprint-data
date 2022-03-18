<script lang="ts">
    import { _ } from 'svelte-i18n';
    export let gwpImpactTotal;
    let gwpFactorThermalCar = 0.107;
    let gwpEquivalentThermalCar = gwpImpactTotal * gwpFactorThermalCar;
</script>


<div>
    <h3 class="title-second">{$_('index.title_equivalent')}</h3>
    <span>{$_('index.label_equivalent')} : {gwpEquivalentThermalCar} kgCO2 eq.</span>
</div>