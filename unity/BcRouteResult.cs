using System;

[Serializable]
public class BcRouteResult
{
    public string correctedInputText;
    public string correctionStatus;
    public string punctuationStatus;
    public string utteranceType;
    public int informationRequestCount;
    public string routingBasisText;
    public string semanticTarget;
    public string intentClass;
    public string routeCategory;
    public string routeCode;
    public float confidence;
}
