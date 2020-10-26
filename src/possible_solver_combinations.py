from python_settings import SettingsDict, SettingsList, SettingsChildPlaceholder, SettingsChoice, SettingsDictEntry, SettingsListEntry, SettingsSolver, SettingsMesh, SettingsComment
# each dict entry corresponds to a cpp-template
# each template-dict can have a ordered list with template_arguments (assuming there are no template_arguments if omitted)

# possible outer templates (runnables) have the key runnable set to True (assuming False if ommited)

# templates that are discretizable in time have discretizableInTime set to True (assuming False if omited)
# "discretizableInTime" in template_arguments will get expanded to all classes, which have discretizableInTime == True

# templates that are a "TimeSteppingScheme" (e.g. all TimeSteppingScheme:: and OperatorSplitting::) have timeSteppingScheme set to True (assuming False if omited)
# "timeSteppingScheme" in template_arguments will get expanded to all classes, which have timeSteppingScheme == True

# templates with optional template_arguments can have the key template_arguments_needed set to the minimal required argument count
# template_arguments_needed is assumed to be len(template_arguments) if template_arguments_needed is omitted
# e.g. in BasisFunction::LagrangeOfOrder and PrescribedValues

# the keyword "Integer" can be used in template_arguments where an integer is expected (e.g. in CellmlAdapter)

# lists of the form [ "Mesh::" ] get auto expanded to [ "Mesh::StructuredRegularFixedOfDimension", "Mesh::Str..", ... ]

# templates added so far:
# TODO add postprocessing Postprocessing::ParallelFiberEstimation
# Postprocessing::StreamlineTracer
# PreciceAdapter::ContractionDirichletBoundaryConditions
# PreciceAdapter::ContractionNeumannBoundaryConditions
# PreciceAdapter::PartitionedFibers
# PreciceAdapter::MuscleContraction MuscleContractionSolver FastMonodomainSolver
# SpatialDiscretization::HyperelasticitySolver
# Control::MultipleInstances
# Control::Coupling
# TODO Control::MultipleCoupling
# Control::LoadBalancing
# Control::MapDofs
# OperatorSplitting::
# CellmlAdapter
# ModelOrderReduction::POD
# ModelOrderReduction::LinearPart
# ModelOrderReduction::ExplicitEulerReduced
# ModelOrderReduction::ImplicitEulerReduced
# FunctionSpace::
# OutputWriter::OutputSurface
# TODO add other OutputWriters
# PrescribedValues
# TimeSteppingScheme::
# TimeSteppingScheme::DynamicHyperelasticitySolver
# TimeSteppingScheme::StaticBidomainSolver
# TimeSteppingScheme::MultidomainSolver
# TimeSteppingScheme::MultidomainWithFatSolver
# TimeSteppingScheme::QuasiStaticNonlinearElasticitySolverFebio
# TimeSteppingScheme::NonlinearElasticitySolverFebio
# TimeSteppingScheme::QuasiStaticLinearElasticitySolver
# TimeSteppingScheme::QuasiStaticNonlinearElasticitySolverChaste
# SpatialDiscretization::FiniteElementMethod
# Mesh::
# BasisFunction::
# Quadrature::
# Equation::

solver = SettingsSolver([
    SettingsDictEntry("solverType", '"gmres"', 'the KSPType of the solver, i.e. which solver to use', 'solver.html#solvertype'),
    SettingsDictEntry("preconditionerType", '"none"', 'the preconditioner type of PETSc to use', 'solver.html#preconditionertype'),
    SettingsDictEntry("relativeTolerance", '1e-5', 'the relative tolerance of the residuum after which the solver is converged', 'solver.html#relativetolerance'),
    SettingsDictEntry("maxIterations", '1e4', 'the maximum number of iterations after which the solver aborts and states divergence', 'solver.html#maxiterations'),
    SettingsDictEntry("dumpFilename", '""',
                      "if this is set to a non-empty string, the system matrix and right hand side vector will be dumped before every linear solve", 'solver.html#dumpfilename'),
    SettingsDictEntry("dumpFormat", '"default"', 'the format in which to export/dump data of matrices and vectors in the file', 'solver.html#dumpformat')
])

outputwriter = SettingsDictEntry("OutputWriter", SettingsList([
    SettingsListEntry(
        SettingsDict([
            SettingsDictEntry("format", '"Paraview"', 'one of Paraview, PythonFile, ExFile, MegaMol, PythonCallback', 'output_writer.html#outputwriter'),
            SettingsDictEntry("filename", '"out/filename"', 'the file name of the output file to write', 'output_writer.html#filename'),
            SettingsDictEntry("outputInterval", '1', 'the interval in which timesteps an actual file should be written', 'output_writer.html#outputinterval'),
            SettingsDictEntry("fileNumbering", '"incremental"', 'incremental or timeStepIndex', 'output_writer.html#filenumbering'),
            SettingsDictEntry("binary", 'True', 'whether to produce binary data files', 'output_writer.html#binary'),
            SettingsDictEntry("fixedFormat", 'True', None, 'output_writer.html#fixedformat'),
            SettingsDictEntry("combineFiles", 'False', None, 'output_writer.html#combinefiles'),
            SettingsChoice([],[
                SettingsDictEntry("onlyNodalValues", 'True', None, None),
            ]),
            SettingsChoice([],[
                SettingsDictEntry("sphereSize", '"0.005*0.005*0.01"', 'ExFile: defines how spheres, used to visualize nodes, will be rendered. The format is x*y*z', 'output_writer.html#exfile'),
            ]),
            SettingsChoice([],[
                SettingsDictEntry("callback", 'callback', 'PythonCallback: python-function to call back to', 'output_writer.html#pythoncallback'),
            ]),
        ])
    )
]), 'specifies a list of output writers that can be used to output geometry field variables in various formats', 'output_writer.html#outputwriter')

timestepping_schemes_ode_common = [
    SettingsChildPlaceholder(0),
    SettingsDictEntry("endTime", '1', 'run() method performs the simulation for t∈[0,endTime]', 'timestepping_schemes_ode.html#endtime-numbertimesteps-and-timestepwidth'),
   SettingsChoice([
       SettingsDictEntry("numberTimeSteps", '10', None, 'timestepping_schemes_ode.html#endtime-numbertimesteps-and-timestepwidth')
   ], [
       SettingsDictEntry("timeStepWidth", '0.001', None, 'timestepping_schemes_ode.html#endtime-numbertimesteps-and-timestepwidth')
   ]),
   SettingsChoice([], [
       SettingsDictEntry("logTimeStepWidthAsKey", '"timestep_width"', 'the time step width of this scheme will be stored under this key in logs/log.csv', 'timestepping_schemes_ode.html#logtimestepwidthaskey-lognumbertimestepsaskey-and-durationlogkey')
   ]),
   SettingsChoice([], [
       SettingsDictEntry("logNumberTimeStepsAsKey", '"timesteps_number"', 'the number of time steps of this scheme will be stored under this key in logs/log.csv', 'timestepping_schemes_ode.html#logtimestepwidthaskey-lognumbertimestepsaskey-and-durationlogkey')
   ]),
   SettingsChoice([], [
       SettingsDictEntry("durationLogKey", '"duration"', 'the total time that has passed for the computation will be stored under this key in logs/log.csv', 'timestepping_schemes_ode.html#logtimestepwidthaskey-lognumbertimestepsaskey-and-durationlogkey')
   ]),
   SettingsDictEntry("timeStepOutputInterval", '100', 'a positive integer value that specifies the interval in which timesteps are printed to standard output', 'timestepping_schemes_ode.html#timestepoutputinterval'),
   SettingsDictEntry("initialValues", '[]', 'list of double values to use as initial values. The solution is set to these values upon initialization', 'timestepping_schemes_ode.html#initialvalues'),
   SettingsDictEntry("dirichletBoundaryConditions", '{}', 'dictionary with degrees of freedom as key and the value as value (i.e. {"dof": value, ...}', 'timestepping_schemes_ode.html#dirichletboundaryconditions-and-inputmeshisglobal'),
   SettingsDictEntry("inputMeshIsGlobal", 'True', 'the degrees of freedom are interpreted in global numbering, if inputMeshIsGlobal is set to True, or in local numbering of the process, if inputMeshIsGlobal is False', 'timestepping_schemes_ode.html#dirichletboundaryconditions-and-inputmeshisglobal'),
   SettingsChoice([], [
       outputwriter
   ]),
   SettingsChoice([], [
       SettingsDictEntry("nAdditionalFieldVariables", '1', 'number of additional field variables that will be created', 'timestepping_schemes_ode.html#nadditionalfieldvariables'),
       SettingsDictEntry("additionalSlotNames", '["connector_slot_1"]', 'list of strings, names for of connector slots for the additional field variables', 'timestepping_schemes_ode.html#additionalslotnames')
   ])
]

operator_splitting_common = timestepping_schemes_ode_common + [
    SettingsDictEntry("connectedSlotsTerm1To2", '[0]', 'list of slots of term 2 that are connected to the slots of term 1', 'output_connector_slots.html#connectedslotsterm1to2-and-connectedslotsterm2to1'),
    SettingsDictEntry("connectedSlotsTerm2To1", '[0]', 'list of slots of term 1 that are connected to the slots of term 2', 'output_connector_slots.html#connectedslotsterm1to2-and-connectedslotsterm2to1'),
    SettingsDictEntry("Term1", SettingsDict([
        SettingsChildPlaceholder(0)
    ])),
    SettingsDictEntry("Term2", SettingsDict([
        SettingsChildPlaceholder(1)
    ]))
]

possible_solver_combinations = {
    "GLOBAL": {
        # template_arguments gets set by cpp_tree.py (to all runnables)
        "python_options": SettingsDict([
            SettingsDictEntry("scenarioName", '"test-scenario"'),
            SettingsDictEntry("logFormat", '"csv"', "csv or json"),
            SettingsDictEntry("meta", SettingsDict(), 'additional fields that will appear in the log'),
            SettingsDictEntry("solverStructureDiagramFile",
                              '"solver_structure.txt"', 'filename of file that will contain a visualization of the solver structure and data mapping', 'output_connector_slots.html#solverstructurediagramfile'),
            SettingsDictEntry("connectedSlots", '[]', None, 'output_connector_slots.html#using-global-slot-names'),
            SettingsDictEntry("mappingsBetweenMeshesLogFile",
                              '""', 'this is the name of a log file that will contain events during creation and mapping', 'mappings_between_meshes.html#mappingsbetweenmesheslogfile'),
            SettingsDictEntry("MappingsBetweenMeshes", '{}', None, 'mappings_between_meshes.html#mappingsbetweenmeshes'),
            SettingsChildPlaceholder(0)
        ])
    },


    "Postprocessing::ParallelFiberEstimation": {
        "runnable": True,
        "template_arguments": [
            ('TODO', ["BasisFunction::"])
        ]
    },
    "Postprocessing::StreamlineTracer": {
        "runnable": True,
        "template_arguments": [
            ('TODO', ["discretizableInTime"])
        ]
    },


    "PreciceAdapter::ContractionDirichletBoundaryConditions": {
        "runnable": True,
        "template_arguments": [
            ('TODO', ["timeSteppingScheme"])
        ]
    },
    "PreciceAdapter::ContractionNeumannBoundaryConditions": {
        "runnable": True,
        "template_arguments": [
            ('TODO', ["timeSteppingScheme"])
        ]
    },
    "PreciceAdapter::PartitionedFibers": {
        "runnable": True,
        "template_arguments": [
            ('TODO', ["timeSteppingScheme"])
        ]
    },
    "PreciceAdapter::MuscleContraction": {
        "runnable": True,
        "template_arguments": [
            ('TODO', ["MuscleContractionSolver"])
        ]
    },
    "MuscleContractionSolver": {
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments_needed": 0,
        "template_arguments": [
            # TODO this should only accept Mesh::StructuredDeformableOfDimension<3>
            # and maybe Mesh::CompositeOfDimension<3>?
            ('TODO', ["Mesh::"])
        ]
    },
    "FastMonodomainSolver": {
        # TODO is this runnable?
        "runnable": True,
        # TODO can this be handled like a timeSteppingScheme?
        "timeSteppingScheme": True,
        "template_arguments": [
            ('TODO', ["Control::MultipleInstances"])
        ]
    },
    "SpatialDiscretization::HyperelasticitySolver": {
        "runnable": True,
        # TODO can this be handled like a timeSteppingScheme?
        "timeSteppingScheme": True,
        "template_arguments_needed": 0,
        "template_arguments": [
            ('TODO', [
             "Equation::SolidMechanics::TransverselyIsotropicMooneyRivlinIncompressible3D"])
            # TODO can this handle more template_arguments?
        ]
    },


    "Control::MultipleInstances": {
        "runnable": True,
        # TODO can this be handled like a timeSteppingScheme?
        "timeSteppingScheme": True,
        "template_arguments": [
            ('TODO', ["timeSteppingScheme"])
        ],
        "python_options": SettingsDict([
            SettingsDictEntry("MultipleInstances", SettingsDict([
                SettingsDictEntry("nInstances", '1'),
                SettingsDictEntry("instances", SettingsList([
                    SettingsListEntry(SettingsDict([
                        SettingsDictEntry("ranks", 'list(range(4))'),
                        SettingsChildPlaceholder(0)
                    ]))
                ])),
                outputwriter
            ]))
        ])
    },


    "Control::LoadBalancing": {
        # TODO is this runnable
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments": [
            ('TODO', ["timeSteppingScheme"])
        ]
    },
    "Control::MapDofs": {
        "runnable": True,
        # TODO can this be handled like a timeSteppingScheme?
        "timeSteppingScheme": True,
        "template_arguments": [
            ('TODO', ["FunctionSpace::"]),
            ('TODO', ["timeSteppingScheme"])
        ]
    },


    "OperatorSplitting::Godunov": {
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments": [
            ('First TimeSteppingScheme', ["timeSteppingScheme"]),
            ('Second TimeSteppingScheme', ["timeSteppingScheme"])
        ],
        "python_options": SettingsDict([
            SettingsDictEntry("GodunovSplitting", SettingsDict(
                operator_splitting_common
            ))
        ])
    },
    "OperatorSplitting::Strang": {
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments": [
            ('First TimeSteppingScheme', ["timeSteppingScheme"]),
            ('Second TimeSteppingScheme', ["timeSteppingScheme"])
        ],
        "python_options": SettingsDict([
            SettingsDictEntry("StrangSplitting", SettingsDict(
                operator_splitting_common
            ))
        ])
    },


    "Control::Coupling": {
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments": [
            ('First TimeSteppingScheme', ["timeSteppingScheme"]),
            ('Second TimeSteppingScheme', ["timeSteppingScheme"])
        ],
        "python_options": SettingsDict([
            SettingsDictEntry("Coupling", SettingsDict(
                operator_splitting_common
            ))
        ])
    },
    "Control::MultipleCoupling": {
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments_needed" : 2,
        "template_arguments": [
            ('First TimeSteppingScheme', ["timeSteppingScheme"]),
            ('Second TimeSteppingScheme', ["timeSteppingScheme"]),
            ('Third TimeSteppingScheme', ["timeSteppingScheme"]),
            ('Fourth TimeSteppingScheme', ["timeSteppingScheme"]),
            ('Fifth TimeSteppingScheme', ["timeSteppingScheme"])
        ],
        "python_options": SettingsDict([
            SettingsDictEntry("MultipleCoupling", SettingsDict(
                timestepping_schemes_ode_common + [
                    SettingsDictEntry("connectedSlotsTerm1To2", 'None', 'this would be the connected slots for a normal Coupling scheme, but here it should be set to None, use global option "connectedSlots" instead', 'output_connector_slots.html#connectedslotsterm1to2-and-connectedslotsterm2to1'),
                    SettingsDictEntry("connectedSlotsTerm2To1", 'None', 'this would be the connected slots for a normal Coupling scheme, but here it should be set to None, use global option "connectedSlots" instead', 'output_connector_slots.html#connectedslotsterm1to2-and-connectedslotsterm2to1'),
                    SettingsDictEntry("Term1", SettingsDict([
                        SettingsChildPlaceholder(0)
                    ])),
                    SettingsDictEntry("Term2", SettingsDict([
                        SettingsChildPlaceholder(1)
                    ])),
                    SettingsDictEntry("Term3", SettingsDict([
                        SettingsChildPlaceholder(2)
                    ])),
                    SettingsDictEntry("Term4", SettingsDict([
                        SettingsChildPlaceholder(3)
                    ])),
                    SettingsDictEntry("Term5", SettingsDict([
                        SettingsChildPlaceholder(4)
                    ]))
                ]
            ))
        ])
    },


    "CellmlAdapter": {
        "discretizableInTime": True,
        "template_arguments_needed": 2,
        "template_arguments": [
            ('Number of states', ["Integer"]),
            ('Number of algebraics', ["Integer"]),
            ('FunctionSpace', ["FunctionSpace::"])
        ],
        "python_options": SettingsDict([
            SettingsDictEntry("CellML", SettingsDict([
                SettingsChoice([
                    SettingsDictEntry("modelFilename", '"../../input/hodgkin_huxley_1952.c"', 'filename of the CellML model file (cellml-XML or c/c++)', 'cellml_adapter.html#modelfilename')
                ], [
                    SettingsDictEntry("libraryFilename", "../lib/model.so", 'filename of a shared object library (.so) that will be used to compute the model', 'cellml_adapter.html#libraryfilename')
                ]),
                SettingsDictEntry("statesInitialValues", '"CellML"', 'list with initial values for each state of the CellML model or "CellML" or "undefined"', 'cellml_adapter.html#statesinitialvalues'),
                SettingsDictEntry("initializeStatesToEquilibrium", 'True', 'if the equilibrium values of the states should be computed before the simulation starts', 'cellml_adapter.html#initializestatestoequilibrium-and-initializestatestoequilibriumtimestepwidth'),
                SettingsDictEntry("initializeStatesToEquilibriumTimestepWidth", '1e-4', 'timestep width to use to solve the equilibrium equation', 'cellml_adapter.html#initializestatestoequilibrium-and-initializestatestoequilibriumtimestepwidth'),
                SettingsChoice([],[
                    SettingsDictEntry("setSpecificParametersFunction", 'set_specific_parameters', 'function name', 'cellml_adapter.html#setspecificparametersfunction-and-setspecificparameterscallinterval')
                ]),
                SettingsChoice([],[
                    SettingsDictEntry("setSpecificParametersFunction", '0', None, 'cellml_adapter.html#setspecificparametersfunction-and-setspecificparameterscallinterval')
                ]),
                SettingsChoice([],[
                    SettingsDictEntry("setSpecificStatesFunction", 'set_specific_states', 'function name', 'cellml_adapter.html#setspecificstatesfunction-and-setspecificstatescallinterval')
                ]),
                SettingsChoice([],[
                    SettingsDictEntry("setSpecificStatesCallInterval", '1', None, 'cellml_adapter.html#setspecificstatesfunction-and-setspecificstatescallinterval')
                ]),
                SettingsChoice([],[
                    SettingsDictEntry("setSpecificStatesCallEnableBegin", '0', None, 'cellml_adapter.html#setspecificstatescallenablebegin-setspecificstatescallfrequency-and-setspecificstatesfrequencyjitter'),
                    SettingsDictEntry("setSpecificStatesCallFrequency", '0.1', None, 'cellml_adapter.html#setspecificstatescallenablebegin-setspecificstatescallfrequency-and-setspecificstatesfrequencyjitter'),
                    SettingsDictEntry("setSpecificStatesFrequencyJitter", '0', None, 'cellml_adapter.html#setspecificstatescallenablebegin-setspecificstatescallfrequency-and-setspecificstatesfrequencyjitter')
                ]),
                SettingsChoice([], [
                    SettingsDictEntry("handleResultFunction", 'handle_result', 'function name', 'cellml_adapter.html#handleresultfunction-and-handleresultcallinterval')
                ]),
                SettingsChoice([], [
                    SettingsDictEntry("handleResultCallInterval", '1', None, 'cellml_adapter.html#handleresultfunction-and-handleresultcallinterval')
                ]),
                SettingsChoice([], [
                    SettingsDictEntry("parametersUsedAsAlgebraic", '[]', 'list of algebraic numbers that will be replaced by parameters', 'cellml_adapter.html#parametersusedasalgebraic')
                ]),
                SettingsChoice([], [
                    SettingsDictEntry("parametersUsedAsConstant", '[]', 'list of indices, which constants in the computation will be replaced by parameters', 'cellml_adapter.html#parametersusedasconstant')
                ]),
                SettingsChoice([], [
                    SettingsDictEntry("algebraicsForTransfer", '[]', 'list of algebraics that should be transferred to the other solver in either a Coupling, GodunovSplitting or StrangSplitting', 'cellml_adapter.html#algebraicsfortransfer-and-statesfortransfer')
                ]),
                SettingsChoice([], [
                    SettingsDictEntry("statesForTransfer", '[]', 'list of states that should be transferred to the other solver in either a Coupling, GodunovSplitting or StrangSplitting', 'cellml_adapter.html#algebraicsfortransfer-and-statesfortransfer')
                ]),
                SettingsChoice([], [
                    SettingsDictEntry("parametersInitialValues", '[]', 'list of values of the parameters. This also defines the number of parameters', 'cellml_adapter.html#parametersinitialvalues')
                ]),
                SettingsChoice([], [
                    SettingsDictEntry("mappings", '{}', None, 'cellml_adapter.html#mappings')
                ]),
                SettingsChoice([
                    SettingsDictEntry("nElements", '0', 'set the number of instances to be computed', 'cellml_adapter.html#meshname')
                ],[
                    SettingsDictEntry("meshName", '"meshX"', 'the mesh to use, to be defined under "Meshes"', 'cellml_adapter.html#meshname')
                ]),
                SettingsDictEntry("stimulationLogFilename", '"out/stimulation.log"', 'file name of an output file that will contain all firing times', 'cellml_adapter.html#stimulationlogfilename'),
                SettingsDictEntry("optimizationType", '"vc"', 'one of simd, vc, openmp', 'cellml_adapter.html#optimizationtype'),
                SettingsChoice([], [
                    SettingsDictEntry("compilerFlags", '"-fPIC -finstrument-functions -ftree-vectorize -fopt-info-vec-optimized=vectorizer_optimized.log -shared"', 'additional compiler flags for the compilation of the source file', 'cellml_adapter.html#compilerflags')
                ]),
                SettingsChoice([], [
                    outputwriter
                ])
            ]))
        ])
    },


    "ModelOrderReduction::POD": {
        "discretizableInTime": True,
        "template_arguments": [
            ('TODO', ["discretizableInTime"]),
            ('TODO', ["ModelOrderReduction::LinearPart"])
        ]
    },
    "ModelOrderReduction::LinearPart": {},
    "ModelOrderReduction::ExplicitEulerReduced": {
        "timeSteppingScheme": True,
        "template_arguments": [
            ('TODO', ["TimeSteppingScheme::ExplicitEuler"])
        ]
    },
    "ModelOrderReduction::ImplicitEulerReduced": {
        "timeSteppingScheme": True,
        "template_arguments": [
            ('TODO', ["TimeSteppingScheme::ImplicitEuler"])
        ]
    },


    "FunctionSpace::FunctionSpace": {
        "template_arguments": [
            ('TODO', ["Mesh::"]),
            ('TODO', ["BasisFunction::"])
        ]
    },


    "TimeSteppingScheme::ExplicitEuler": {
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments": [
            ('DiscretizableInTime', ["discretizableInTime"])
        ],
        "python_options": SettingsDict([
            SettingsDictEntry("ExplicitEuler", SettingsDict(
                timestepping_schemes_ode_common
            ))
        ])
    },
    "TimeSteppingScheme::ImplicitEuler": {
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments": [
            ('DiscretizableInTime', ["discretizableInTime"])
        ],
        "python_options": SettingsDict([
            SettingsDictEntry("ImplicitEuler", SettingsDict(
                timestepping_schemes_ode_common + [
                    solver,
                    SettingsDictEntry("timeStepWidthRelativeTolerance", '1e-10', 'tolerance for the time step width which controls when the system matrix has to be recomputed', 'timestepping_schemes_ode.html#impliciteuler'),
                    SettingsChoice([], [
                        SettingsDictEntry("timeStepWidthRelativeToleranceAsKey", '"relative_tolerance"', 'timeStepWidthRelativeTolerance will be stored under this key in logs/log.csv', 'timestepping_schemes_ode.html#impliciteuler')
                    ]),
                    SettingsChoice([], [
                        SettingsDictEntry("durationInitTimeStepLogKey", '"duration_init_time_step"', 'duration for the time step initialization  will be stored under this key in logs/log.csv', 'timestepping_schemes_ode.html#impliciteuler')
                    ])
                ]
            ))
        ])
    },
    "TimeSteppingScheme::Heun": {
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments": [
            ('DiscretizableInTime', ["discretizableInTime"])
        ],
        "python_options": SettingsDict([
            SettingsDictEntry("Heun", SettingsDict(
                timestepping_schemes_ode_common
            ))
        ])
    },
    "TimeSteppingScheme::HeunAdaptive": {
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments": [
            ('DiscretizableInTime', ["discretizableInTime"])
        ],
        "python_options": SettingsDict([
            SettingsDictEntry("HeunAdaptive", SettingsDict(
                timestepping_schemes_ode_common + [
                    SettingsDictEntry("tolerance", '0.1', 'tolerance for the estimated error. It is guaranteed, that the error is always smaller than this value', 'timestepping_schemes_ode.html#tolerance'),
                    SettingsDictEntry("minTimeStepWidth", '1e-6', 'the minimum timestepwidth to use', 'timestepping_schemes_ode.html#mintimestepwidth'),
                    SettingsDictEntry("timeStepAdaptOption", '"regular"', 'method for the adaptive time step width computation (regular or modified)', 'timestepping_schemes_ode.html#timestepadaptoption'),
                    SettingsChoice([], [
                        SettingsDictEntry("lowestMultiplier", '1000', 'minimum number of timesteps to perform in the time span for the "modified" method', 'timestepping_schemes_ode.html#lowestmultiplier')
                    ])
                ]
            ))
        ])
    },
    "TimeSteppingScheme::CrankNicolson": {
        "timeSteppingScheme": True,
        "template_arguments": [
            ('DiscretizableInTime', ["discretizableInTime"])
        ],
        "python_options": SettingsDict([
            SettingsDictEntry("CrankNicolson", SettingsDict(
                timestepping_schemes_ode_common + [
                    solver,
                    SettingsDictEntry("timeStepWidthRelativeTolerance", '1e-10', 'tolerance for the time step width which controls when the system matrix has to be recomputed', 'timestepping_schemes_ode.html#lowestmultiplier'),
                    SettingsChoice([], [
                        SettingsDictEntry("timeStepWidthRelativeToleranceAsKey", '"relative_tolerance"', 'timeStepWidthRelativeTolerance will be stored under this key in logs/log.csv', 'timestepping_schemes_ode.html#lowestmultiplier')
                    ]),
                    SettingsChoice([], [
                        SettingsDictEntry("durationInitTimeStepLogKey", '"duration_init_time_step"', 'duration for the time step initialization  will be stored under this key in logs/log.csv', 'timestepping_schemes_ode.html#lowestmultiplier')
                    ])
                ]
            ))
        ])
    },


    "TimeSteppingScheme::RepeatedCall": {
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments": [
            # TODO does this really accept any timeSteppingScheme
            ('TODO', ["timeSteppingScheme"])
        ]
    },
    "TimeSteppingScheme::RepeatedCallStatic": {
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments": [
            ('TODO', ["SpatialDiscretization::FiniteElementMethod"])
        ]
    },
    # specalizedSolvers:
    "TimeSteppingScheme::DynamicHyperelasticitySolver": {
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments_needed": 0,
        "template_arguments": [
            ('TODO', ["Equation::"]),
            # TODO this should only accept Mesh::StructuredDeformableOfDimension<3>
            ('TODO', ["Mesh::StructuredRegularFixedOfDimension"])
        ]
    },
    "TimeSteppingScheme::StaticBidomainSolver": {
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments": [
            ('TODO', ["SpatialDiscretization::FiniteElementMethod"]),
            ('TODO', ["SpatialDiscretization::FiniteElementMethod"])
        ]
    },
    "TimeSteppingScheme::MultidomainSolver": {
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments": [
            ('TODO', ["SpatialDiscretization::FiniteElementMethod"]),
            ('TODO', ["SpatialDiscretization::FiniteElementMethod"])
        ]
    },
    "TimeSteppingScheme::MultidomainWithFatSolver": {
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments": [
            ('TODO', ["SpatialDiscretization::FiniteElementMethod"]),
            ('TODO', ["SpatialDiscretization::FiniteElementMethod"]),
            ('TODO', ["SpatialDiscretization::FiniteElementMethod"])
        ],
        "python_options": SettingsDict([
            # TODO
            SettingsDictEntry("MultidomainSolver", SettingsDict([
                SettingsDictEntry("PotentialFlow", SettingsDict([
                    SettingsChildPlaceholder(0)
                ])),
                SettingsDictEntry("Activation", SettingsDict([
                    SettingsChildPlaceholder(1)
                ])),
                SettingsDictEntry("Fat", SettingsDict([
                    SettingsChildPlaceholder(2)
                ]))
            ]))
        ])
    },
    "TimeSteppingScheme::QuasiStaticNonlinearElasticitySolverFebio": {
        "runnable": True,
        "timeSteppingScheme": True
    },
    "TimeSteppingScheme::NonlinearElasticitySolverFebio": {
        "runnable": True,
        "timeSteppingScheme": True
    },
    "TimeSteppingScheme::QuasiStaticLinearElasticitySolver": {
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments": [
            ('TODO', ["SpatialDiscretization::FiniteElementMethod"])
        ]
    },
    "TimeSteppingScheme::QuasiStaticNonlinearElasticitySolverChaste": {
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments": [
            ('TODO', ["Integer"])
        ]
    },


    "PrescribedValues": {"runnable": True,
                         "timeSteppingScheme": True,
                         "template_arguments_needed": 1,
                         "template_arguments": [
                             ('TODO', ["FunctionSpace::FunctionSpace"]),
                             ('TODO', ["1", "2", "3"]),
                             ('TODO', ["1", "2", "3"])
                         ]
                         },



    "OutputWriter::OutputSurface": {
        "runnable": True,
        # TODO can this be handled like a timeSteppingScheme?
        "timeSteppingScheme": True,
        "template_arguments": [
            ('TODO', ["timeSteppingScheme",
                      "SpatialDiscretization::FiniteElementMethod"])
        ],
        "python_options": SettingsDict([
            SettingsDictEntry("OutputSurface", SettingsDict([
                # TODO
                # SettingsDictEntry("OutputWriter", SettingsList([
                # ])),
                SettingsDictEntry("face", '["1-"]'),
                SettingsChildPlaceholder(0)
            ]))
        ])
    },


    "SpatialDiscretization::FiniteElementMethod": {
        "runnable": True,
        "discretizableInTime": True,
        "template_arguments": [
            ('Mesh', ["Mesh::"]),
            ('BasisFunction', ["BasisFunction::"]),
            ('Quadrature', ["Quadrature::"]),
            ('Equation', ["Equation::"])
        ],
        "python_options": SettingsDict([
            SettingsDictEntry("FiniteElementMethod", SettingsDict([
                SettingsChildPlaceholder(0),
                SettingsDictEntry("slotName", '""', 'specifies the name of the slot that contains the solution variable', 'finite_element_method.html#slotname'),
                SettingsDictEntry("prefactor", '1', 'a scalar multiplier of the Laplace operator term, i.e. c in c⋅Δu or c⋅∇⋅(A∇u)', 'finite_element_method.html#prefactor'),
                SettingsDictEntry("rightHandSide", '{}', 'right hand side vector f (either as list or as dict)', 'finite_element_method.html#righthandside'),
                SettingsDictEntry("dirichletBoundaryConditions", '{}', 'a dict with {<dof no>: <value>} entries', 'boundary_conditions.html#dirichlet-boundary-conditions'),
                SettingsDictEntry("dirichletOutputFilename", 'None', 'write Dirichlet Boundary conditions to .vtp file', 'boundary_conditions.html#dirichlet-output-filename'),
                SettingsDictEntry("neumannBoundaryConditions", '[]', None, 'boundary_conditions.html#neumann-boundary-conditions'),
                SettingsDictEntry(
                    "updatePrescribedValuesFromSolution", 'False', 'if set to true, the values that are initially set in the solution field variable are used as the prescribed values at the dofs in dirichletBoundaryConditions', 'finite_element_method.html#updateprescribedvaluesfromsolution'),
                SettingsDictEntry("inputMeshIsGlobal", 'True', 'together with rightHandSide it specifies whether the given values are interpreted as local values or global values in the context of a parallel execution on multiple processes', 'finite_element_method.html#inputmeshisglobal'),
                SettingsChoice([], [
                    SettingsDictEntry("diffusionTensor", '[]', 'for anisotropic diffusion, the diffusion tensor can be given as a list of double valus in row-major order', 'finite_element_method.html#diffusiontensor')
                ]),
                solver,
                SettingsChoice([], [
                    outputwriter
                ]),
            ]))
        ])
    },

    "Mesh::StructuredRegularFixedOfDimension": {
        "template_arguments": [
            ("Dimension", ["1", "2", "3"])
        ],
        "python_options": SettingsDict([
            SettingsMesh([
                SettingsDictEntry("nElements", SettingsList(['1', '1']), 'the number of elements of the mesh in the coordinate directions', 'mesh.html#nelements'),
                SettingsDictEntry("physicalExtent", '[1.0, 1.0]', 'the “size” of the mesh in physical units (e.g. meters if SI units are used), in the coordinate directions', 'mesh.html#physicalextent'),
                SettingsDictEntry("inputMeshIsGlobal", 'True', 'whether the values of nElements and physicalExtent describe the global domain (True) or the local subdomain (False) in parallel execution', 'mesh.html#inputmeshisglobal')
            ])
        ])
    },

    "Mesh::StructuredDeformableOfDimension": {
        "template_arguments": [
            ("Dimension", ["1", "2", "3"])
        ],
        "python_options": SettingsDict([
            SettingsMesh([
                SettingsDictEntry("nElements", SettingsList(['1', '1']), 'the number of elements of the mesh in the coordinate directions', 'mesh.html#id1'),
                SettingsDictEntry("inputMeshIsGlobal", 'True', 'whether the values of nElements and the nodePositions describe the global domain (True) or the local subdomain (False) in parallel execution', 'mesh.html#id2'),
                SettingsChoice([
                    SettingsDictEntry("physicalExtent", '[1.0, 1.0]', 'the “size” of the mesh in physical units (e.g. meters if SI units are used), in the coordinate directions', 'mesh.html#physicalextent'),
                    SettingsDictEntry("physicalOffset", '[0.0, 0.0]', 'offset all node positions by the given vector', 'mesh.html#structureddeformable')
                ], [
                    SettingsDictEntry("nodePositions", '[[0,0,0], [0,0,0]]', 'specify all node positions', 'mesh.html#nodepositions')
                ])
            ])
        ])
    },

    "Mesh::UnstructuredDeformableOfDimension": {
        "template_arguments": [
            ('Dimension', ["1", "2", "3"])
        ],
        "python_options": SettingsDict([
            SettingsMesh([
                SettingsChoice([
                    SettingsDictEntry("elements", '[[0,0]]', 'list of nodes, each node is [node no, version-at-that-node no] or just node-no then it assumes version no 0', 'mesh.html#elements'),
                    SettingsDictEntry("nodePositions", '[[0,0]]', 'list of positions of the nodes, each node position is a list with maximum three entries for the components in x,y and z direction', 'mesh.html#id5')
                ], [
                    SettingsDictEntry("exelem", "filename.exelem", 'the filename of the exelem file', 'mesh.html#exelem'),
                    SettingsDictEntry("exnode", "filename.exnode", 'the filename of the exnode file', 'mesh.html#exnode')
                ])
            ])
        ])
    },

    "Mesh::CompositeOfDimension": {
        "template_arguments": [
            ('Dimension', ["1", "2", "3"])
        ],
        "python_options" : SettingsDict([
            SettingsDictEntry("meshName", '["meshX", "meshY"]', 'a list containing all mesh names of the submeshes', 'mesh.html#compositeofdimension-d')
        ])
    },


    "BasisFunction::CompletePolynomialOfDimensionAndOrder": {
        "template_arguments": [
            ('Dimension', ["1", "2", "3"]),
            ('Order', ["0", "1", "2"])
        ]
    },
    "BasisFunction::Hermite": {},
    "BasisFunction::LagrangeOfOrder": {
        "template_arguments_needed": 0,
        "template_arguments": [
            ('TODO', ["1", "2"])
        ]
    },
    # TODO are there BasisFunction::Mixed?


    "Quadrature::None": {},
    "Quadrature::ClenshawCurtis": {
        "template_arguments": [
            ('TODO', ["1", "2", "3", "4", "5", "6", "7", "64"])
        ]
    },
    "Quadrature::Gauss": {
        "template_arguments": [
            ('TODO', ["1", "2", "3", "4", "5", "6", "7",
                      "8", "10", "12", "16", "20", "24", "64"])
        ]
    },
    "Quadrature::NewtonCotes": {
        "template_arguments": [
            ('TODO', ["1", "2", "3", "4", "5", "6", "7", "8"])
        ]
    },
    "Quadrature::TensorProduct": {
        "template_arguments": [
            ('TODO', ["1", "2", "3"]),
            ('TODO', ["Quadrature::"])
        ]
    },
    # TODO are there Quadrature::Mixed?
    # "Quadrature::Mixed" : {
    #    "template_arguments" : [
    #       [ ],
    #       [ "Quadrature::ClenshawCurtis", "Quadrature::Gauss", "Quadrature::NewtonCotes" ]
    #    ]
    # },


    "Equation::Dynamic::IsotropicDiffusion": {},
    "Equation::Dynamic::AnisotropicDiffusion": {},
    "Equation::Dynamic::DirectionalDiffusion": {},
    "Equation::Static::Laplace": {},
    "Equation::Static::GeneralizedLaplace": {},
    "Equation::Static::LinearElasticity": {},
    "Equation::Static::LinearElasticityActiveStress": {},
    # TODO are these correct?
    "Equation::SolidMechanics::MooneyRivlinIncompressible3D": {},
    "Equation::SolidMechanics::TransverselyIsotropicMooneyRivlinIncompressible3D": {},
    "Equation::SolidMechanics::TransverselyIsotropicMooneyRivlinIncompressibleActive3D": {},
    "Equation::SolidMechanics::HyperelasticTendon": {},
    "Equation::SolidMechanics::HyperelasticityBase": {},
    "Equation::Static::Poisson": {},
    "Equation::Static::GeneralizedPoisson": {},
}
