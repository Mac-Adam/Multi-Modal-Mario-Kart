// Copyright Epic Games, Inc. All Rights Reserved.

#include "Unreal_projectWheelFront.h"
#include "UObject/ConstructorHelpers.h"

UUnreal_projectWheelFront::UUnreal_projectWheelFront()
{
	AxleType = EAxleType::Front;
	bAffectedBySteering = true;
	MaxSteerAngle = 45.f;
}