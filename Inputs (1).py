'Inputs'

from scipy.optimize import least_squares

def inputs(**kwargs):
    
    #Feedstock prices and values
    Feedstock_table = {
        'SWG': { #Switchgrass
                    'grass_price': 63.55/1000, #$/kg w.b.
                    'CH4_yield_grass': 139.86, #mL CH4/g VS
                     'Moisture_grass': 0.15, #Percentage of moisture in grass % w.b.
                     'VS_grass': 0.917, #Percentage of volatile solids in grass % w.b. or % of d.m. depends on grass, see Stream.py
                     'Carbon_grass': 0.4693, #Percentage of carbon in grass % w.b.
                     'Nitrogen_grass': 0.0046, #Percentage of nitrogen in grass % w.b.
                     'Biomass_yield_grass': 15.69, #Biomass yield, w.b. Mg/ha
                     'Land_available': 4640, #Land available to grow, ha
                     'Phosphorus_grass': 0.00415, #Percentage of phosphorus in grass % w.b.
                     'handling': 'baled', #Handling method, either baled or ensiled
            },
        'CORN': { #Corn stover
            'grass_price': 52.19/1000, 'CH4_yield_grass': 168.89,
                     'Moisture_grass': 0.052, 'VS_grass': 0.8802, 'Carbon_grass': 0.4326,
                     'Nitrogen_grass': 0.006, 'Biomass_yield_grass': 11.71, 'Land_available': 38184, #4147,
                     'Phosphorus_grass': 0.000654, 'handling': 'baled',
            },
        'WR': { #Winter rye
            'grass_price': 102/1000, 'CH4_yield_grass': 249.15,
                     'Moisture_grass': 0.65, 'VS_grass': 0.923, 'Carbon_grass': 0.37,
                     'Nitrogen_grass': 0.01, 'Biomass_yield_grass': 6.725, 'Land_available': 2410.49, #3053.5,
                     'Phosphorus_grass': 0.0042, 'handling': 'ensiled',
            }
    }
    
    # Define defaults
    
    default = {
        
        #SCENARIO DEFINITION
        
        'Use_manure': True, #True if manure is included as feedstock
        'Use_grass': True, #True if grass is included as feedstock
        
        'cows': 10000, #Plant capacity in number of cows
        
        'collection_fraction_manure': 0.6, #Fraction of manure collected from the farms
        'collection_fraction_grass': 0.2, #Fraction of grass collected from cropland
        
        'feedstock_land_fraction': {'SWG': 0.0, # 1.0 Use 100% of switchgrass' available land
                          'CORN': 0.0, # 0.4 Use 40% of corn stover's available land
                          'WR': 1.0}, # 0.0 Use 0% of winter rye's available land

        #OPERATIONAL PARAMETERS
        'manure_inlet_temperature': 20, #°C
        'grass_inlet_temperature': 14, #°C
        'water_inlet_temperature': 10, #°C
        'external_temperature': 14, #°C
        'Total_solids_digester':0.10, #10% of total solids in the digester
        'HRT': 22, # Desired Hydraulic Retention Time in days
        'Temperature_digester': 37, #°C
        'Cap_factor': 0.95, #0.95 Assumption of the capacity factor of the plant with employees on site
        'km_to_pipeline': 2, #km
        'Max_digester_volume': 8000, #m3
        'Ammonia_digestate_yield': 0.7, #70% of organic nitrogen converted to soluble ammonia in the digester
        'Heat_mixtank': False, #True if mixing tank before the digester will be heating the slurry. If not it will be only a mixing tank
        'Biogas_upgrading': True, #True if biogas upgrading to RNG is included
        'CO2_sequestration': False, #True if CO2 sequestration process is included
        'Nutrient_recovery': False, #True if nutrient recovery (struvite precipitation) is included

        #STORAGE
        'Manure_storage': True, #True if a manure pit needs to be constructed in the plant
        'Grass_storage': True, #True if a grass storage unit (slab for bales) needs to be constructed in the plant
        'Digestate_storage': True, #True if a digestate storage unit needs to be constructed in the plant
        'Manure_storage_time': 3, #3 days of storage prior to AD
        'Grass_storage_time': 3, #3 days of storage prior to AD
        'Digestate_storage_time': 240, #8 months, 240 days of storage after AD

        #TRANSPORTATION
        'Truck_capacity': 22.68, #Mg per truck manure or digestate
        'LRS_distance': 15, #km Distance of Land River Segment to the Centralized AD
        'County_distance': 15, #km Average distance from farm to centralized AD within the county
        'Truck_bales': 36, #Bales
        'Truck_capacity_bulk_grass': 25.8, #m3 simulating Silage dump box for bulk transportation
        'CO2_transportation_distance': 129, #km Distance to transport CO2 to sequestration or utilization site
        'CO2_truck_capacity': 22, #Mg per truck CO2
        'Tortuosity_factor': 1.3, # How much transport path deviates from a straight line
        'CO2_injection_cost': 20.50, # $/Mg CO2 cost of storing CO2 underground

        #Nutrient Recovery
        'Recovery_efficiency_P': 0.918, #Percentage of phosphorus recovered as struvite
        'NaOH_dose': 0.640, #kg/m3 of NaOH per liquid digestate

        #METHANE YIELDS
        'CH4_yield_manure': 134.15, #mL CH4/g VS
        'CH4_yield_grass': None, #mL CH4/g VS, depends on grass type
        
        #PRICE AND ECONOMIC PARAMETERS
        'RIN_price': 2.97, #$/gal #3.1045,
        'solid_digestate_price': 0.03525, #$/kg
        'liquid_digestate_price': 0.937, # $/kg NH4N (Plant available nitrogen in the digestate)
        'electricity_price': 0.1733, #$/kWh
        'water_price': 0.00295, #$/gal
        'manure_price': 0.937, # $/kg NH4N (Plant available nitrogen in the manure)
        'Natural_gas_price': 4.29, #$/1000 cubic feet
        'grass_price': None, #$/kg
        'diesel_price': 3.61, #$/gal
        'MgO_price': 2.18, #$/kg
        'Struvite_price': 1.10, #$/kg
        'CO2_sequestration_price': 85/1000, #$/Mg CO2
        'NaOH_price': 0.518, #$/kg NaOH
        'Salary_operator': 19.07, #$/h operator wage
        
        'Grant_percentage': 0, #%0.5 = 50% grant
        
        #FEEDSTOCK CHARACTERISTICS
        #DAIRY MANURE
        'Lactating_cows': 0.85, #Percentage of lactating cows in the farm
        'Manure_moisture_lactating': 0.87, #Percentage of moisture in lactating cows
        'Manure_moisture_dry': 0.87, #Percentage of moisture in dry cows
        'Manure_VS_lactating': 0.109, #Percentage % w.b. of VS in lactating cows
        'Manure_VS_dry': 0.111, #Percentage % w.b. of VS in dry cows
        'Manure_Carbon_lactating': 0.060, #Percentage of carbon in lactating cows (% of w.b.)
        'Manure_Carbon_dry': 0.061, #Percentage of carbon in dry cows (% of w.b.)
        'Manure_Nitrogen_lactating': 0.007, #Percentage of nitrogen in lactating cows % w.b.
        'Manure_Nitrogen_dry': 0.006, #Percentage of nitrogen in dry cows % d.m.
        'Manure_Phosphorus_lactating': 0.00115, #Percentage of phosphorus in lactating cows % w.b.
        'Manure_Phosphorus_dry': 0.000789, #Percentage of phosphorus in dry cows % d.m.
    }
    default.update(kwargs)

    feedstock_land_fraction = default['feedstock_land_fraction']

    if default['Use_grass']:
        
        for feedstock, fraction in feedstock_land_fraction.items():
            if fraction < 0 or fraction > 1:
                raise ValueError(f'{feedstock} land fraction must be between 0 and 1.')
        
        active_feedstocks = {
            feedstock: fraction
            for feedstock, fraction in feedstock_land_fraction.items()
            if fraction > 0
        }

        feedstock_properties = {
            feedstock: Feedstock_table[feedstock].copy()
            for feedstock in feedstock_land_fraction
        }
    
    else :
        active_feedstocks = {}
        feedstock_properties = {
            feedstock: Feedstock_table[feedstock].copy()
            for feedstock in Feedstock_table
        }
    
    default['active_feedstocks'] = active_feedstocks
    default['feedstock_properties'] = feedstock_properties
    default['feedstock_table'] = Feedstock_table

    return default

def get_stream_prices(water_price,
                      manure_price,
                      RIN_price,
                      solid_digestate_price,
                      liquid_digestate_price,
                      Natural_gas_price,
                      Diesel_price):
    
    water_price = water_price * (1 / (0.003785 * 1000))  # $/kg
    Diesel_price = Diesel_price *(1/3.785) #$/L
    #grass_price = grass_price/1000    # $/kg

    'RIN price'
    Energy_content_ethanol = 75583 #BTU/gallon of ethanol
    Energy_content_natgas = 1.036 #mmBTU/thousand cubic feet of natural gas. 
    Energy_content_methane = 50 #MJ/kg of methane
    Energy_content_methane = Energy_content_methane * 947.81 #MJ/kg to BTU/kg
    RIN_price_kg = (RIN_price/Energy_content_ethanol)*Energy_content_methane #USD/kg of methane
    Natural_gas_kg = (Natural_gas_price/Energy_content_natgas)*(Energy_content_methane/10**6) #USD/kg of methane - assuming natural gas as mostly methane
    RNG_price = RIN_price_kg + Natural_gas_kg #USD/kg of methane

    return {
        'water': water_price,
        'manure': manure_price,
        'RNG': RNG_price,
        'Natural_gas': Natural_gas_kg,
        'solid_digestate': solid_digestate_price,
        'liquid_digestate': liquid_digestate_price,
        'diesel_price': Diesel_price
    }

def stream_densities(active_feedstocks=None, use_manure=True, use_grass=True):
    # Densities in BioSTEAM depends on the components of the stream.
    # I need to calculate the value for Volatile solids and Ash content to get the overall density.
    # More in my notes "Density"

    water_density = 998.7 #kg/m3 at 17°C (half of manure and grass inlet temperatures)
    
    density_basis = {}
    
    if use_manure:
        density_basis['Manure'] = {
            'target_density': 1001.858,
            'Water': 0.878,
            'VS': 0.1030,
            'Ash': 0.0190,
        }

    grass_density_data = {
        'SWG': {
            'target_density': 1195,
            'Water': 0.15,
            'VS': 0.7752,
            'Ash': 0.0748,
        },
        'CORN': {
            'target_density': 861.7,
            'Water': 0.0524,
            'VS': 0.8802,
            'Ash': 0.0674,
        },
        'WR': {
            'target_density': 1195,
            'Water': 0.0409,
            'VS': 0.8846,
            'Ash': 0.0745,
        },
    }

    if use_grass and active_feedstocks:
        for feedstock in active_feedstocks:
            density_basis[feedstock] = grass_density_data[feedstock]

    if not density_basis:
        raise ValueError('At least one feedstock must be active for density calculation.')

    
    def residuals(vars):
        VS_density, Ash_density = vars

        errors = []

        for name, data in density_basis.items():
            predicted_density = 1 / (
                data['Water'] / water_density
                + data['VS'] / VS_density
                + data['Ash'] / Ash_density
            )

            errors.append(predicted_density - data['target_density'])

        return errors

    result = least_squares(
        residuals,
        x0=[1200, 2500],
        bounds=([1, 1], [10000, 10000])
    )

    VS_density, Ash_density = result.x

    print(f"Fitted VS density: {VS_density:.2f} kg/m3")
    print(f"Fitted Ash density: {Ash_density:.2f} kg/m3")
    print(f"Density fit error: {result.cost}")
    print(f"Density fit success: {result.success}")

    return {
        'VS': VS_density,
        'Ash': Ash_density,
    }


