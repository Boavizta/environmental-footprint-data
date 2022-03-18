<script lang="ts">

    import DataGrid from "./DataGrid.svelte";
    import LifetimeInput from "./LifetimeInput.svelte";
    import RegionPicker from "./RegionPicker.svelte";
    import RequestButton from "./RequestButton.svelte";
    import EquivalentImpacts from "./EquivalentImpacts.svelte";

    let datagrid;
    let lifetime;
    let region;
    let disabledSearchButton;
    let rows_selection;

    function impactScope3():number{
        let scope3 = 0;
        rows_selection.forEach(row => scope3 += row["Total (kgCO2eq)"]*row["Manufacturing"]);
        return scope3
    }

    function electricalImpactFactor(location: Location):number {
        return 0;
    }

    function impactScope2():number{
        let scope2 = 0;
        if(lifetime == undefined && region == undefined){
            rows_selection.forEach(row => scope2 += row["Total (kgCO2eq)"]*row["Use"]);
        }else if (lifetime != undefined && region == undefined){
            rows_selection.forEach(row => scope2 += ((row["Total (kgCO2eq)"]*row["Use"])/row["Lifetime"])*lifetime);
        }else if (lifetime == undefined && region != undefined){
            rows_selection.forEach(row => scope2 += row["Yearly TEC (kWh)"]*row["Lifetime"]*electricalImpactFactor(location));
        }else if (lifetime != undefined && region != undefined){
            rows_selection.forEach(row => scope2 += row["Yearly TEC (kWh)"]*lifetime*electricalImpactFactor(location));
        }
        return scope2
    }

</script>
<div>
<DataGrid bind:datagrid/>
<RegionPicker bind:region/>
<LifetimeInput bind:lifetime/>
<RequestButton bind:disabledSearchButton/>
<EquivalentImpacts gwpImpactTotal="200"/>
</div>
