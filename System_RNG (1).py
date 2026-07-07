
'System RNG'

from Inputs import inputs

'Inputs.py file'
data = inputs()

def create_system(data):

    # CALLING OTHER FILES TO MAIN SYSTEM FILE

    from Inputs import get_stream_prices, stream_densities
    from Chemicals import create_chemicals
    from Stream import manure_properties, grass_properties, water_slurry_properties
    from Process_settings import Cp_manure, Cp_grass_mixture, k_manure, k_grass_mixture, k_water, external_temperature, Cp_water
    from Reactions import ideal_gas_volume_mL, biogas_methane_conversions
    from Units import ManureStorageTank, GrassStorageTank, Shredder, MixingTank, ContinousFermentation, H2SRemovalUnit, Biogas_cooling, SolidsSeparator 
    from Units import DigestateStorageTank, Membrane_Separation, BoilerUnit, CHPUnit, MultistageCompressorCH4, MultistageCompressorCO2, CO2_Liquefier
    from Units import Drum1, Drum2, StruvitePrecipitation, StruviteFiltration, BaleProcessor
    
    import biosteam as bst
    from biosteam import units
    from biosteam import Splitter, Flash

    #CALLING DATA FROM OTHER FILES

    prices = get_stream_prices(water_price=data['water_price'],
                            manure_price=data['manure_price'],
                            RIN_price=data['RIN_price'],
                            solid_digestate_price=data['solid_digestate_price'],
                            liquid_digestate_price=data['liquid_digestate_price'],
                            Natural_gas_price=data['Natural_gas_price'],
                            Diesel_price=data['diesel_price'])


    RNG_price_value = prices['RNG']
    Nat_gas = prices['Natural_gas']

    densities = stream_densities(
        active_feedstocks=data['active_feedstocks'],
        use_manure=data['Use_manure'],
        use_grass=data['Use_grass'],
        )

    'Chemicals.py file'
    
    chemicals = create_chemicals(VS_density=densities['VS'],
                                 Ash_density=densities['Ash'])
    bst.settings.set_thermo(chemicals)


    'Stream.py file'
    manure_data = manure_properties(cows = data['cows'],
                                    manure_T= data['manure_inlet_temperature'],
                                    price = prices['manure'],
                                    lactating_cows= data['Lactating_cows'],
                                    moisture_lactating= data['Manure_moisture_lactating'],
                                    moisture_dry= data['Manure_moisture_dry'],
                                    VS_lactating= data['Manure_VS_lactating'],
                                    VS_dry= data['Manure_VS_dry'],
                                    Carbon_lactating= data['Manure_Carbon_lactating'],
                                    Carbon_dry= data['Manure_Carbon_dry'],
                                    Nitrogen_lactating= data['Manure_Nitrogen_lactating'],
                                    Nitrogen_dry= data['Manure_Nitrogen_dry'],
                                    Phosphorus_lactating= data['Manure_Phosphorus_lactating'],
                                    Phosphorus_dry= data['Manure_Phosphorus_dry'],
                                    collection_fraction = data['collection_fraction_manure'],
                                    cap_factor = data['Cap_factor'],
                                    use_manure = data['Use_manure'],
                                    )


    grass_data = grass_properties(feedstock_land_fraction = data['feedstock_land_fraction'],
                                feedstock_properties = data['feedstock_properties'],
                                use_grass = data['Use_grass'],
                                grass_T = data['grass_inlet_temperature'],
                                grass_storage_time = data['Grass_storage_time'],
                                collection_fraction_grass = data['collection_fraction_grass'],
                                truck_bales = data['Truck_bales'],
                                truck_volume = data['Truck_capacity_bulk_grass'],
                                cap_factor = data['Cap_factor'],
                                )

    water_data = water_slurry_properties(manure_per_day = manure_data['manure_per_day'],
                                        grass_per_day = grass_data['totals']['grass_per_day'],
                                        manure_solids= manure_data['manure_solids'],
                                        grass_water = grass_data['totals']['flow_grass_water'],
                                        water_T = data['water_inlet_temperature'],
                                        price = prices['water'],
                                        TS_digester = data['Total_solids_digester']
                                        )

    Carbon_Nitrogen_ratio = (manure_data['manure_carbon']+ grass_data['totals']['grass_carbon'])/(manure_data['manure_nitrogen']+grass_data['totals']['grass_nitrogen'])

    'Process_settings.py file'

    Cp_manure_data = Cp_manure(manure_T = data['manure_inlet_temperature'],
                                manure_water_frac = manure_data['water_frac'])

    Cp_grass_data = Cp_grass_mixture(grass_data = grass_data)

    Cp_water_data = Cp_water()

    # Cp_mixture_data = Cp_mixture(water_flowrate= water_data['water_flowrate'],
    #                             manure_flowrate = manure_data['flowrate'] if data['Use_manure'] else 0,
    #                             grass_data = grass_data if data['Use_grass'] else None,
    #                             Cp_manure_value = Cp_manure_data['Cp_manure'],
    #                             )

    k_manure_data = k_manure(manure_T = data['manure_inlet_temperature'],
                            manure_water_frac = manure_data['water_frac'])
    
    k_grass_data = k_grass_mixture(grass_data = grass_data)

    k_water_data = k_water()

    # k_mixture_data = k_mixture(water_flowrate= water_data['water_flowrate'],
    #                         manure_flowrate = manure_data['flowrate'] if data['Use_manure'] else 0,
    #                         grass_data = grass_data if data['Use_grass'] else None,
    #                         k_manure_value = k_manure_data['k_manure'],
    #                         )

    external_temperature_data = external_temperature(external_temperature_value = data['external_temperature'])

    'Reactions.py file'

    Ideal_gas_data = ideal_gas_volume_mL(T_K = data['Temperature_digester'] + 273.15)  # K
    Methane_data = biogas_methane_conversions(manure_flowrate = manure_data['flowrate'] if data['Use_manure'] else 0,
                                            grass_data = grass_data if data['Use_grass'] else None,
                                            manure_vsolids= manure_data['manure_vsolids'] if data['Use_manure'] else 0,
                                            CH4_yield_manure = data['CH4_yield_manure'],
                                            Gas_volume = Ideal_gas_data['Gas_volume']) # mL CH4/g VS


    #BIOSTEAM SETTINGS

    'Settings'
    steam_utility = bst.settings.get_agent('low_pressure_steam') #Using low pressure steam because our heating needs are not that high.
    bst.settings.heating_agents = [steam_utility]
    steam_utility.heat_transfer_efficiency = 1.0   ##This is heat transfer efficiency. The boiler already takes this into account, so it can be ignored.
    steam_utility.heat_transfer_price = 0 

    cooling_utility = bst.settings.get_agent('chilled_brine')   #Chilled brine was used for the gas cooling stage in order to get the gas cool enough to remove all the moisture.
    bst.settings.cooling_agents = [cooling_utility]
    cooling_utility.heat_transfer_efficiency = 0.8

    bst.settings.electricity_price = data['electricity_price'] #Electricity price in $/kWh
    bst.stream_utility_prices['Natural gas'] = prices['Natural_gas'] #Natural gas price in $/kg
    #natural_gas = bst.settings.get_heating_agent('natural_gas') #Natural gas is used for the CHP unit, so we need to set it as a heating agent.
    #natural_gas.heat_transfer_price = prices['Natural_gas']/55000 #Natural gas price in $/kg

    #SCENARIO CONFIGURATION

    'Scenarios - Plant unit operations' # True/False to include/exclude certain unit operations in the plant design
    
    manure_storage = data['Manure_storage'] #True if a manure pit needs to be constructed in the plant
    grass_storage = data['Grass_storage'] #True if a grass storage unit (slab for bales) needs to be constructed in the plant
    digestate_storage = data['Digestate_storage'] #True if a digestate storage unit needs to be constructed in the plant
    heat_mixtank = data['Heat_mixtank'] #True if mixing tank before the digester will be heating the slurry. If not it will be only a mixing tank
    upgrading = data['Biogas_upgrading'] #True if biogas upgrading to RNG is included
    CO2_sequestration = data['CO2_sequestration'] #True if CO2 sequestration process is included
    nutrient_recovery = data['Nutrient_recovery'] #True if nutrient recovery (struvite precipitation) is included

    #STREAMS

    'Grasses'
    grass_streams = [
        grass_data['by_feedstock']['SWG']['stream'],
        grass_data['by_feedstock']['CORN']['stream'],
        grass_data['by_feedstock']['WR']['stream'],
        ]

    'Mixing tank streams' #This is to help BioSTEAM recognize the streams and for it to calculate the amount of water needed
    Manure = bst.Stream('Manure', units='kg/hr')
    Grass = bst.Stream('Grass', units='kg/hr')
    Water = bst.Stream('Water', units='kg/hr', price=prices['water'])

    'Utility streams'
    MgO = bst.Stream('MgO_stream', units='kg/hr', phase='s', price=data['MgO_price']) #For struvite precipitation
    NaOH = bst.Stream('NaOH_stream', units='kg/hr', phase='l', price=data['NaOH_price']) #For struvite precipitation

    'Recycle stream'
    Recirculated_slurry = bst.Stream('Recirculated_slurry', units='kg/hr', phase='l')
    Recirculated_slurry.imass['H2O'] = 5000 # kg/hr initial guess for the first run

    Recirculated_CO2 = bst.Stream('Recirculated_CO2', units='kg/hr', phase='g')
    
    'Product streams'
    RNG = bst.Stream('RNG', units='kg/hr', phase='g', price=prices['RNG'])
    solid_digestate = bst.Stream('Solid_Digestate', units='kg/hr', phase='s', price=prices['solid_digestate'])
    liquid_digestate = bst.Stream('Liquid_Digestate', units='kg/hr', phase='l')
    struvite = bst.Stream('Struvite', units='kg/hr', phase='s', price=data['Struvite_price'])
    CO2_sequestered = bst.Stream('CO2_sequestered', units='kg/hr', phase='l', price=data['CO2_sequestration_price'])   

    #UNIT OPERATIONS
    
    'Pre-treatment'

    Manure_Pit = ManureStorageTank(manure_storage=manure_storage,
                                use_manure=data['Use_manure'],
                                storage_time = data['Manure_storage_time'],
                                ID='Manure_Pit', ins=[manure_data['stream']], outs='Manure')

    # Set number of cows
    Manure_Pit.number_of_cows = data['cows']

    Manure_Pump = units.Pump('Manure_Pump', ins=Manure_Pit-0, outs=Manure)

    Grass_Storage = GrassStorageTank(grass_storage=grass_storage,
                                     use_grass=data['Use_grass'],
                                     storage_bales=grass_data['totals']['bales_for_storage'],
                                     storage_time = data['Grass_storage_time'],
                                     storage_ensiled = grass_data['totals']['storage_ensiled'],
                                     cap_factor = data['Cap_factor'],
                                     ID='Grass_Storage', ins=grass_streams, outs='baled_grass')

    Bale_processor = BaleProcessor('Grass_Debaler', Grass_Storage-0, outs='grass',
                                   baled_flowrate=grass_data['totals']['baled_flowrate'])
    
    Grass_Shredder = Shredder('Grass_Shredder', Bale_processor-0, outs=Grass)

    Mixing_Tank = MixingTank(heat_mixtank = heat_mixtank,
                                Cp_manure_value = Cp_manure_data['Cp_manure'],
                                Cp_grass_value = Cp_grass_data['Cp_grass'],
                                Cp_water = Cp_water_data,
                                k_grass_value = k_grass_data['k_grass'],
                                k_manure_value = k_manure_data['k_manure'],
                                k_water_value = k_water_data,
                                temperature_digester = data['Temperature_digester'],
                                external_temperature_value = data['external_temperature'],
                                water_temperature = data['water_inlet_temperature'],
                                TS_digester = data['Total_solids_digester'],
                                ID='Mix_Tank', ins=[Manure, Grass, Water, Recirculated_slurry], outs='Slurry', T=data['Temperature_digester']+273.15)

    'Anaerobic Digestion'

    Digester = ContinousFermentation(upgrading = upgrading,
                                     hrt_hr = data['HRT']*24,
                                     Mix_tank = Mixing_Tank,
                                     external_temperature_value = data['external_temperature'],
                                     temperature_digester = data['Temperature_digester'],
                                     CH4_mass_yield = Methane_data['CH4_mass_yield'],
                                     CO2_mass_yield = Methane_data['CO2_mass_yield'],
                                     Max_volume = data['Max_digester_volume'],
                                     Ammonia_yield = data['Ammonia_digestate_yield'],
                                     ID ='Digester', ins= Mixing_Tank-0, outs=('Biogas', 'Digestate'), T=data['Temperature_digester']+273.15, tau = data['HRT']*24)

    'Biogas Treatment'
    
    Biogas_Splitter = units.Splitter('Biogas_loss', 
                                    ins=Digester-0, 
                                    outs=('Raw_Biogas','Methane_losses'),  # Two outputs
                                    split={'CH4': 0.98, 'CO2': 1.0, 'Water': 1.0})  


    Moisture_Removal = Biogas_cooling('Moisture_Removal', ins = Biogas_Splitter-0, outs=('Dry_Biogas'), T=data['external_temperature']+273.15, rigorous=True, cool_only=True)
    
    Water_trap = units.Splitter('Water_trap', ins=Moisture_Removal-0, outs=('Water','Dry_Gas'), split={'Water': 1.0, 'CH4': 0, 'CO2': 0})

    #H2S_Removal = H2SRemovalUnit('H2S_Removal', ins=Water_trap-1, outs=('Biogas'))

    "Biogas Upgrading to RNG"

    Gas_Upgrading = Membrane_Separation(ID='Gas_Upgrading', ins=Water_trap-1, outs = ('RNG', 'CO2'), cap_factor=data['Cap_factor']) 

    RNG_Compressor = MultistageCompressorCH4(ID='RNG_Compressor', ins=Gas_Upgrading-0, outs=RNG, pr=1.857, n_stages=2, eta=0.80, vle=False)

    'Digestate Treatment'

    Dewater = SolidsSeparator('Solids_Separator', ins = (Digester-1), outs=(solid_digestate, 'Liquid_stream'), split=dict(Ash=0.49, VolatileSolids=0.49, NH4N=0.25, PO4P=0.17, N_org=0.49), moisture_content=0.60)

    Recycle_loop = Splitter('Recirculation', ins=(Dewater-1), outs=('Recycle_digestate', 'Liquid_digestate'), split=0.5)

    Digestate_Pump = units.Pump('Liq_Digestate_pump', ins=(Recycle_loop-0), outs=Recirculated_slurry)

    digestate_to_storage = Recycle_loop-1 # Liquid digestate to storage. Creating a stream to change the digestate storage input based on nutrient recovery scenario. If nutrient recovery goes to Struvite precipitation, if not goes to storage directly.         

    'Auxiliary Units'

    Boiler = BoilerUnit(ID = 'Boiler', ins = ('Natural_gas','Water'), 
                        boiler_efficiency=0.8, 
                        natural_gas_price=prices['Natural_gas'], 
                        water_price = prices['water'], 
                        satisfy_system_electricity_demand=False, 
                        water_temperature=data['water_inlet_temperature'],
                        Cp_H2O=Cp_water(),
                        Digester_unit=Digester)

    'CO2 Capture and Storage'

    if CO2_sequestration == True:

        CO2_compressor = MultistageCompressorCO2('CO2_MultistageCompressor', ins=Gas_Upgrading-1, outs='CO2_compressed', pr=2.1407, n_stages=4, eta=0.80, vle=False)

        CO2_Mixer = units.Mixer('CO2_Mixer', ins=[CO2_compressor-0, Recirculated_CO2], outs='CO2_for_storage')

        Liquefier = CO2_Liquefier('CO2_Liquefier', ins=CO2_Mixer-0, outs='Liquefied_stream', T=-27+273.15, cool_only=True)

        Drum_1 = Drum1('Drum1', ins=Liquefier-0, outs=['Gases', 'Liquified_CO2'], P=17e5, T=-27+273.15, CO2_recovery=0.983)

        Drum_2 = Drum2('Drum2', ins=Drum_1-1, outs=[Recirculated_CO2, CO2_sequestered], P=17e5, T=-30+273.15, CO2_stored=0.90, cap_factor = data['Cap_factor'])

    'Nutrient recovery'

    if nutrient_recovery == True:
        
        ChemicalPrecipitation = StruvitePrecipitation('Struvite_Precipitation', ins=[Recycle_loop-1, MgO, NaOH], outs=['Struvite_slurry'], efficiency=data['Recovery_efficiency_P'], dose=data['NaOH_dose'])

        Filtration = StruviteFiltration('Struvite_Filtration', ins=[ChemicalPrecipitation-0], outs=['liquid_N', struvite])

        digestate_to_storage = Filtration-0 # Change digestate to storage input to liquid digestate from filtration unit if nutrient recovery is included.


    Digestate_storage = DigestateStorageTank(digestate_storage=digestate_storage,
                                storage_time = data['Digestate_storage_time'],
                                liq_digestate_price = data['liquid_digestate_price'],
                                ID='Digestate_Pit', ins=digestate_to_storage, outs=liquid_digestate)     

    'Run system'

    path = [Manure_Pit, Manure_Pump, Grass_Storage, Bale_processor, Grass_Shredder, Mixing_Tank, Digester, Dewater, Recycle_loop, Digestate_Pump,
            Biogas_Splitter, Moisture_Removal, Water_trap, Gas_Upgrading, RNG_Compressor, Boiler, Digestate_storage]

    if nutrient_recovery == True:
        path += [ChemicalPrecipitation, Filtration, Digestate_storage]
    if CO2_sequestration == True:
        path += [CO2_compressor, CO2_Mixer, Liquefier, Drum_1, Drum_2, CO2_Mixer]
        system_sys = bst.System('RNG_plat', path = path, recycle=[Recirculated_slurry, Recirculated_CO2])
    else:
        system_sys = bst.System('RNG_plat', path = path, recycle=Recirculated_slurry)

    return system_sys, prices, manure_data, grass_data, water_data, Carbon_Nitrogen_ratio, Digester, RNG_price_value, Nat_gas, liquid_digestate, CO2_sequestered, RNG_Compressor, nutrient_recovery, CO2_sequestration, Gas_Upgrading, solid_digestate

def run_model(data):
    system_sys, prices, manure_data, grass_data, water_data, Carbon_Nitrogen_ratio, Digester, RNG_price_value, Nat_gas, liquid_digestate, CO2_sequestered, RNG_Compressor, nutrient_recovery, CO2_sequestration, Gas_Upgrading, solid_digestate = create_system(data)
    system_sys.simulate()

    #print(f"Digester feed mass flow: {Digester.ins[0].F_mass:.2f} kg/hr")
    #Digester = system_sys.flowsheet.unit.Digester
    #Digester = system_sys.flowsheet.unit.Moisture_Removal.results()
    biogas_flow = Digester.outs[0].F_mass
    RNG_production_mass = RNG_Compressor.outs[0].F_mass #Main product, RNG
    liquid_digestate_flow = liquid_digestate.F_mass
    CO2_sequestered_flow = CO2_sequestered.F_mass
    biogas_per_hour = Gas_Upgrading.metric_flow # Nm3/h
    RNG_per_year = Gas_Upgrading.annual_energy_BTU *(1055.06/1000) #GJ/year
    Solid_digestate_year = solid_digestate.F_mass * 24 * (365/1000) # Mg/year
    Liquid_digestate_year = liquid_digestate.F_mass * 24 * (365/1000) # Mg/year
    Raw_input_year = manure_data['flowrate'] * 24 * (365/1000) + grass_data['totals']['flowrate'] * 24 * (365/1000) # Mg/year
    #print(f"Digester feed mass flow: {Digester.outs[0].F_mass:.2f} kg/hr")
    
    # from Process_settings import reactor_variables
    # reactor = reactor_variables(slurry=water_data['slurry_flowrate'])
    
    'Transport.py file'

    from Transport import Transport

    T = Transport()

    transport = T.truck_transportation(truck_capacity = data['Truck_capacity'],
                            one_way_distance = data['LRS_distance'],
                            diesel_price = prices['diesel_price'],
                            labor_cost = data['Salary_operator'],
                            tortuosity_factor = data['Tortuosity_factor'],
                            manure_per_day = manure_data['manure_per_day'],
                            plant_cap_factor = data['Cap_factor'],
                            liquid_digestate = liquid_digestate_flow,
                            county_distance = data['County_distance'],
                            grass_per_day = grass_data['totals']['grass_per_day'],
                            trips_per_year_grass = grass_data['totals']['trips_per_year_grass'],
                            )
    
    CO2_transport = T.CO2_transportation(diesel_price = prices['diesel_price'],
                            tortuosity_factor = data['Tortuosity_factor'],
                            labor_cost = data['Salary_operator'],
                            CO2_transportation_distance = data['CO2_transportation_distance'],
                            CO2_truck_capacity = data['CO2_truck_capacity'],
                            CO2_sequestered = CO2_sequestered_flow,
                            plant_cap_factor = data['Cap_factor'],
                            CO2_injection_cost = data['CO2_injection_cost'])
    
    transport_cost = transport['Total_annual_cost'] + CO2_transport['Annual_cost_CO2'] # Total transportation cost

    Manure_transport = transport['Cost_per_Mg_km_manure']
    Grass_transport = transport['Cost_per_Mg_km_grass']

    'TEA.py file'

    from TEA import AD_TEA

    tea = AD_TEA(system                 =   system_sys,
                IRR                     =   0.06,                       # Internal rate of return
                duration                =   (2025, 2045),               # Start and end year
                depreciation            =   'MACRS7',                   # Number of years
                income_tax              =   0.285,                     # PA income tax
                operating_days          =   365*data['Cap_factor'],     # Operating days per year
                construction_schedule   =   (0.4, 0.6), 
                WC_over_FCI             =   0.05,                       #5% of fixed capital cost
                labor_cost              =   data['Salary_operator'],    #Operator wage
                RNG_production          =   RNG_production_mass,        #Main product production rate
                Nutrient_recovery_units =   nutrient_recovery,          #Nutrient recovery
                CO2_sequestration_units =   CO2_sequestration,          #CO2 sequestration
                pipeline_injection_cost =   0,                          #Pipeline installed capital cost, installed cost of interconnection equipment
                investment_tax_credit   =   0.4,                        #Investment tax credit
                upgrading_cost          =   True,                       #Upgrading cost, if any
                km_to_pipeline          =   data['km_to_pipeline'],     #Distance to pipeline in km)
                Grant_assistance        =   True,                       #Grant assistance, if any
                Grant_percentage        =   data['Grant_percentage'],   #Grant percentage value
                Transportation          =   transport_cost,             #Transportation cost 
    )

    labor = tea.labor_cost

    npv = tea.NPV
    irr = tea.solve_IRR()
    tci = tea.TCI

    #print("NPV: ", npv) # Net present value
    #print("IRR: ", irr) # Internal rate of return
    system_sys.save_report('Manure_Rye_10K_2.xlsx')
    #system_sys.diagram(format='png')
    # print("C/N ratio: ", Carbon_Nitrogen_ratio)
    #system_sys.diagram()

    return {'NPV': npv, 'IRR': irr, 'TCI': tci, 'CN_ratio': Carbon_Nitrogen_ratio, 
            'biogas_kg_hr': biogas_flow, 
            #'RNG': RNG_price_value, #'Natural_gas': Nat_gas, 
            'Manure_input': manure_data['flowrate'],
            'Grass_input': grass_data['totals']['flowrate'],
            'Raw_input_year': Raw_input_year,
            'Biogas_per_hour': biogas_per_hour,
            'RNG_per_year': RNG_per_year,
            'Liquid_digestate_per_year': Liquid_digestate_year,
            'Solid_digestate_per_year': Solid_digestate_year,
            'Manure_transport_cost': Manure_transport,
            'Grass_transport_cost': Grass_transport,
            'Area_grass_ha': grass_data['totals']['area_grass'],
            #'Cows_per_LRS': manure_data['N_cows_LRS'],
            #'Grass_flow_kg_hr': grass_data['flowrate'],
            #'Flow_year': grass_data['totals']['flow_per_year'],
            'Total_transportation_cost': transport_cost,
            #'Labor': labor
            }
    #return {'NPV': npv, 'IRR': irr, 'TCI': tci}
    #return Digester

run_model(data)
