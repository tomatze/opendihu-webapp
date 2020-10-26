from python_settings import SettingsDict, SettingsList, SettingsChildPlaceholder, SettingsChoice, SettingsDictEntry, SettingsListEntry, SettingsSolver, SettingsMesh
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
possible_solver_combinations = {
    "GLOBAL": {
        "python_options": SettingsDict([
            SettingsDictEntry("scenarioName", '"test-scenario"'),
            SettingsDictEntry("logFormat", '"csv"', "csv or json"),
            SettingsDictEntry("solverStructureDiagramFile",
                              '"solver_structure.txt"'),
            SettingsDictEntry("mappingsBetweenMeshesLogFile",
                              '"mappings_between_meshes.txt"'),
            SettingsDictEntry("MappingsBetweenMeshes", '{}'),
            #SettingsDictEntry("Meshes", '{}'),
            #SettingsDictEntry("Solvers", '{}'),
            SettingsDictEntry("meta", SettingsDict([
                # TODO add meta
                SettingsDictEntry("partitioning", '""')
            ])),
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
                ]))
            ]))
        ])
    },
    "Control::Coupling": {
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments": [
            ('TODO', ["timeSteppingScheme"]),
            ('TODO', ["timeSteppingScheme"])
        ]
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


    "OperatorSplitting::Strang": {
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments": [
            ('TODO', ["timeSteppingScheme"]),
            ('TODO', ["timeSteppingScheme"])
        ],
        "python_options": SettingsDict([
            SettingsDictEntry("StrangSplitting", SettingsDict([
                SettingsDictEntry("timeStepWidth", '1e-1'),
                SettingsDictEntry("endTime", '1000.0'),
                SettingsDictEntry("Term1", SettingsDict([
                    SettingsChildPlaceholder(0)
                ])),
                SettingsDictEntry("Term2", SettingsDict([
                    SettingsChildPlaceholder(1)
                ])),
                SettingsChoice([], [
                    SettingsDictEntry("Term3", SettingsDict([
                        SettingsChildPlaceholder(2)
                    ])),
                ]),
                SettingsChoice([], [
                    SettingsDictEntry("Term4", SettingsDict([
                        SettingsChildPlaceholder(3)
                    ])),
                ]),
                SettingsChoice([], [
                    SettingsDictEntry("Term5", SettingsDict([
                        SettingsChildPlaceholder(4)
                    ])),
                ])
            ]))
        ])
    },
    "OperatorSplitting::Godunov": {
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments": [
            ('TODO', ["timeSteppingScheme"]),
            ('TODO', ["timeSteppingScheme"])
        ]
    },


    "CellmlAdapter": {
        "discretizableInTime": True,
        "template_arguments_needed": 1,
        "template_arguments": [
            ('TODO', ["Integer"]),
            ('TODO', ["Integer"]),
            ('TODO', ["FunctionSpace::"])
        ]
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
            ('TODO', ["discretizableInTime"])
        ]
    },
    "TimeSteppingScheme::ImplicitEuler": {
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments": [
            ('TODO', ["discretizableInTime"])
        ]
    },
    "TimeSteppingScheme::Heun": {
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments": [
            ('TODO', ["discretizableInTime"])
        ],
        "python_options": SettingsDict([
            SettingsDictEntry("Heun", SettingsDict([
                SettingsDictEntry("endTime", '1'),
                SettingsDictEntry("timeStepWidth", '0.001'),
                SettingsDictEntry("numberTimeSteps", '10'),
            ]))
        ])
    },
    "TimeSteppingScheme::HeunAdaptive": {
        "runnable": True,
        "timeSteppingScheme": True,
        "template_arguments": [
            ('TODO', ["discretizableInTime"])
        ]
    },
    "TimeSteppingScheme::CrankNicolson": {
        "timeSteppingScheme": True,
        "template_arguments": [
            ('TODO', ["discretizableInTime"])
        ]
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
            ('TODO', ["Mesh::"]),
            ('TODO', ["BasisFunction::"]),
            ('TODO', ["Quadrature::"]),
            ('TODO', ["Equation::"])
        ],
        "python_options": SettingsDict([
            SettingsDictEntry("FiniteElementMethod", SettingsDict([
                SettingsChildPlaceholder(0),
                SettingsDictEntry("prefactor", '1'),
                SettingsDictEntry("rightHandSide", '{}'),
                SettingsDictEntry("dirichletBoundaryConditions", '{}'),
                SettingsDictEntry("dirichletOutputFilename", 'None'),
                SettingsDictEntry("neumannBoundaryConditions", '[]'),
                SettingsDictEntry(
                    "updatePrescribedValuesFromSolution", 'False'),
                SettingsDictEntry("inputMeshIsGlobal", 'True'),
                SettingsSolver([
                    SettingsDictEntry("solverType", '"gmres"'),
                    SettingsDictEntry("preconditionerType", '"none"'),
                    SettingsDictEntry("relativeTolerance", '1e-5'),
                    SettingsDictEntry("maxIterations", '1e4'),
                    SettingsDictEntry("dumpFilename", '""',
                                      "no filename means dump is disabled"),
                    SettingsDictEntry("dumpFormat", '"default"')
                ]),
                SettingsChoice([], [
                    SettingsDictEntry("diffusionTensor", '[]')
                ])
            ]))
        ])
    },

    "Mesh::StructuredRegularFixedOfDimension": {
        "template_arguments": [
            ("dimension", ["1", "2", "3"])
        ],
        "python_options": SettingsDict([
            SettingsMesh([
                SettingsDictEntry("nElements", SettingsList(['0', '1'])),
                SettingsDictEntry("physicalExtent", '[1.0, 1.0]'),
                SettingsDictEntry("inputMeshIsGlobal", 'True')
            ])
        ])
    },
    "Mesh::StructuredDeformableOfDimension": {
        "template_arguments": [
            ("dimension", ["1", "2", "3"])
        ],
        "python_options": SettingsDict([
            SettingsMesh([
                SettingsDictEntry("nElements", SettingsList(['0', '1'])),
                SettingsDictEntry("inputMeshIsGlobal", 'True'),
                SettingsChoice([
                    SettingsDictEntry("physicalExtent", '[2.5, 5.0]'),
                    SettingsDictEntry("physicalOffset", '[0.5, 0.0]')
                ], [
                    SettingsDictEntry("nodePositions", '[[0,0,0], [0,0,0]]')
                ])
            ])
        ])
    },
    "Mesh::UnstructuredDeformableOfDimension": {
        "template_arguments": [
            ('TODO', ["1", "2", "3"])
        ]
    },
    "Mesh::CompositeOfDimension": {
        "template_arguments": [
            ('TODO', ["1", "2", "3"])
        ]
    },


    "BasisFunction::CompletePolynomialOfDimensionAndOrder": {
        "template_arguments": [
            ('TODO', ["1", "2", "3"]),
            ('TODO', ["0", "1", "2"])
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
